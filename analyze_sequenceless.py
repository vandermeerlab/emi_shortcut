import numpy as np
import copy
import random
import scipy
import pickle
import os
import nept

from loading_data import get_data
from analyze_tuning_curves import get_only_tuning_curves
from plots_decoding import (plot_session,
                            plot_likelihood_overspace,
                            plot_counts_merged,
                            plot_counts_averaged,
                            plot_summary_individual)
from utils_maze import get_zones

# Set random seeds
random.seed(0)
np.random.seed(0)


class Session:
    """A collection of LikelihoodsAtTaskTime for each session

        Parameters
        ----------
        task_times : dict of TaskTime

    """

    def __init__(self, position, task_labels, zones):
        self.position = position
        self.task_labels = task_labels
        for task_label in task_labels:
            setattr(self, task_label, TaskTime([], [], [], zones))

    def pickle(self, save_path):
        with open(save_path, 'wb') as fileobj:
            print("Saving " + save_path)
            pickle.dump(self, fileobj)

    def n_tasktimes(self):
        return len(self.task_labels)


class TaskTime:
    """A set of decoded likelihoods for a given task time

        Parameters
        ----------
        likelihoods : np.array
            With shape (ntimebins, nxbins, nybins)
        zones : dict of Zones

        Attributes
        ----------
        likelihoods : np.array
            With shape (ntimebins, nxbins, nybins)

    """

    def __init__(self, tuning_curves, swrs, likelihoods, zones):
        self.tuning_curves = tuning_curves
        self.swrs = swrs
        self.likelihoods = likelihoods
        self.zones = zones

    def sums(self, zone_label):
        return np.nansum(self.likelihoods[:, :, self.zones[zone_label]], axis=2)

    def means(self, zone_label):
        return np.nanmean(self.likelihoods[:, :, self.zones[zone_label]], axis=2)

    def maxes(self, zone_label):
        return np.nanmax(self.likelihoods[:, :, self.zones[zone_label]], axis=2)


def get_likelihoods(info, swr_params, task_labels, n_shuffles=0, save_path=None):
    _, position, spikes, lfp, _ = get_data(info)

    zones = dict()
    zones["u"], zones["shortcut"], zones["novel"] = get_zones(info, position, subset=True)
    combined_zones = zones["u"] + zones["shortcut"] + zones["novel"]
    zones["other"] = ~combined_zones

    if n_shuffles > 0:
        n_passes = n_shuffles
    else:
        n_passes = 1

    session = Session(position, task_labels, zones)

    tuning_curves_fromdata = get_only_tuning_curves(info, position, spikes, info.task_times["phase3"])

    tc_shape = tuning_curves_fromdata.shape

    phase_for_zthresh = "pauseB"

    swrs = nept.detect_swr_hilbert(lfp,
                                   fs=info.fs,
                                   z_thresh=info.lfp_z_thresh,
                                   merge_thresh=swr_params["merge_thresh"],
                                   min_length=swr_params["min_length"],
                                   times_for_z=nept.Epoch(info.task_times[phase_for_zthresh].start,
                                                          info.task_times[phase_for_zthresh].stop))

    swrs = nept.find_multi_in_epochs(spikes, swrs, min_involved=swr_params["min_involved"])

    rest_epochs = nept.rest_threshold(position, thresh=12., t_smooth=0.8)

    for task_label in task_labels:
        epochs_of_interest = info.task_times[task_label].intersect(rest_epochs)

        phase_swrs = epochs_of_interest.overlaps(swrs)
        phase_swrs = phase_swrs[phase_swrs.durations >= 0.05]

        phase_likelihoods = np.zeros((n_passes, phase_swrs.n_epochs, tc_shape[1], tc_shape[2]))
        phase_tuningcurves = np.zeros((n_passes, tc_shape[0], tc_shape[1], tc_shape[2]))
        for n_pass in range(n_passes):

            if n_shuffles > 0:
                tuning_curves = np.random.permutation(tuning_curves_fromdata)
            else:
                tuning_curves = tuning_curves_fromdata

            phase_tuningcurves[n_pass, ] = tuning_curves
            tuning_curves = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

            if phase_swrs.n_epochs == 0:
                phase_likelihoods = np.ones((n_passes, 1, tc_shape[1], tc_shape[2])) * np.nan
            else:
                counts_data = []
                counts_time = []
                t_windows = []

                for n_timebin, (start, stop) in enumerate(zip(phase_swrs.starts,
                                                              phase_swrs.stops)):
                    t_window = stop - start  # 0.1 for running, 0.025 for swr

                    sliced_spikes = [spiketrain.time_slice(start, stop) for spiketrain in spikes]

                    these_counts = nept.bin_spikes(sliced_spikes,
                                                   start,
                                                   stop,
                                                   dt=t_window,
                                                   gaussian_std=0.0075,
                                                   normalized=False,
                                                   lastbin=True)

                    counts_data.append(these_counts.data)
                    counts_time.append(these_counts.time)
                    t_windows.append(t_window)

                counts = nept.AnalogSignal(np.vstack(counts_data), np.hstack(counts_time))
                likelihood = nept.bayesian_prob(counts,
                                                tuning_curves,
                                                binsize=t_windows,
                                                min_neurons=3,
                                                min_spikes=1)

                phase_likelihoods[n_pass] = likelihood.reshape(phase_swrs.n_epochs, tc_shape[1], tc_shape[2])

        tasktime = getattr(session, task_label)
        tasktime.likelihoods = phase_likelihoods
        tasktime.tuning_curves = phase_tuningcurves
        tasktime.swrs = phase_swrs

    if save_path is not None:
        session.pickle(save_path)

    return session


def limit_by_n_swr(session, task_labels, n_swr_thresh, zone_label="u"):
    session_copy = copy.deepcopy(session)

    for task_label in task_labels:
        if getattr(session_copy, task_label).swrs.n_epochs < n_swr_thresh:
            zone_shape = getattr(session_copy, task_label).zones[zone_label].shape
            getattr(session_copy, task_label).likelihoods = np.ones((1, 1, zone_shape[0], zone_shape[1])) * np.nan

    return session_copy


def get_decoded_swr_plots(infos, group, pickle_filepath, output_filepath,
                          n_swr_thresh=10, n_shuffles=100, update_cache=False):

    dont_save_pickle = False
    plot_individual = False
    plot_individual_passthresh = False
    plot_overspace = False
    plot_summary = True

    percentile_thresh = 95

    colours = dict()
    colours["u"] = "#2b8cbe"
    colours["shortcut"] = "#31a354"
    colours["novel"] = "#d95f0e"
    colours["other"] = "#bdbdbd"

    # swr params
    swr_params = dict()
    swr_params["merge_thresh"] = 0.02
    swr_params["min_length"] = 0.05
    swr_params["min_involved"] = 4

    task_labels = ["prerecord", "pauseA", "pauseB", "postrecord"]
    zone_labels = ["u", "shortcut", "novel", "other"]

    true_sessions = []
    shuffled_sessions = []
    passthresh_sessions = []
    passthresh_counts = []

    for info in infos:
        print(info.session_id)

        # Get true data
        true_path = os.path.join(pickle_filepath, info.session_id + "_likelihoods_true.pkl")

        # Remove previous pickle if update_cache
        if update_cache:
            if os.path.exists(true_path):
                os.remove(true_path)

        # Load pickle if it exists, otherwise compute and pickle
        if os.path.exists(true_path):
            print("Loading pickled true likelihoods...")
            compute_likelihoods = False
            with open(true_path, 'rb') as fileobj:
                true_session = pickle.load(fileobj)
        else:
            if dont_save_pickle:
                true_path = None
            true_session = get_likelihoods(info,
                                           swr_params,
                                           task_labels,
                                           n_shuffles,
                                           save_path=true_path)

        true_sessions.append(true_session)

        sessions_copy = []
        for session in true_sessions:
            session_copy = limit_by_n_swr(session, task_labels, n_swr_thresh)
            sessions_copy.append(session_copy)
        true_sessions = sessions_copy

        # Get shuffled data
        shuffled_path = os.path.join(pickle_filepath,
                                     info.session_id + "_likelihoods_shuffled-%03d.pkl" % n_shuffles)

        # Remove previous pickle if update_cache
        if update_cache:
            if os.path.exists(shuffled_path):
                os.remove(shuffled_path)

        # Load pickle if it exists, otherwise compute and pickle
        if os.path.exists(shuffled_path):
            print("Loading pickled shuffled likelihoods...")
            with open(shuffled_path, 'rb') as fileobj:
                shuffled_session = pickle.load(fileobj)
        else:
            if dont_save_pickle:
                shuffled_path = None
            shuffled_session = get_likelihoods(info,
                                               swr_params,
                                               task_labels,
                                               n_shuffles=n_shuffles,
                                               save_path=shuffled_path)

        shuffled_sessions.append(shuffled_session)
        sessions_copy = []
        for session in true_sessions:
            session_copy = limit_by_n_swr(session, task_labels, n_swr_thresh)
            sessions_copy.append(session_copy)
        shuffled_sessions = sessions_copy

        if plot_individual:
            filepath = os.path.join(output_filepath, "individual")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            plot_summary_individual(info, true_session, shuffled_session,
                                    zone_labels, task_labels, colours, filepath)

        if plot_overspace:
            filepath = os.path.join(output_filepath, "overspace")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            plot_likelihood_overspace(info, true_session, task_labels, colours, filepath)

        keep_idx = {task_label: [] for task_label in task_labels}
        passthresh_count = {task_label: {zone_label: 0 for zone_label in zone_labels} for task_label in task_labels}

        for task_label in task_labels:
            for zone_label in zone_labels:
                zones = getattr(true_session, task_label).zones
                true_sums = np.array(getattr(true_session, task_label).sums(zone_label))
                shuffled_sums = np.array(getattr(shuffled_session, task_label).sums(zone_label))
                if true_sums.size <= 1 and np.isnan(true_sums).all():
                    continue
                elif getattr(true_session, task_label).swrs.n_epochs == 0:
                    continue
                else:
                    for idx in range(true_sums.shape[1]):
                        percentile = scipy.stats.percentileofscore(np.sort(shuffled_sums[:, idx]), true_sums[:, idx][0])
                        if percentile >= percentile_thresh:
                            keep_idx[task_label].append(idx)
                            passthresh_count[task_label][zone_label] += 1

        passthresh_counts.append(passthresh_count)

        passthresh_path = os.path.join(pickle_filepath, info.session_id + "_likelihoods_true_passthresh.pkl")

        if update_cache:
            if os.path.exists(passthresh_path):
                os.remove(passthresh_path)

        if os.path.exists(passthresh_path):
            print("Loading pickled passthresh likelihoods...")
            with open(passthresh_path, 'rb') as fileobj:
                passthresh_session = pickle.load(fileobj)
                passthresh_sessions.append(passthresh_session)

        else:
            passthresh_session = Session(true_session.position, task_labels, zones)

            for task_label in task_labels:
                passthresh_idx = np.sort(np.unique(keep_idx[task_label]))
                if len(passthresh_idx) > 0:
                    passthresh_likelihoods = np.array(getattr(true_session, task_label).likelihoods)[:, passthresh_idx]
                    passthresh_swrs = getattr(true_session, task_label).swrs[passthresh_idx]
                else:
                    passthresh_likelihoods = np.ones(
                        (1, 1) + getattr(true_session, task_label).likelihoods.shape[2:]) * np.nan
                    passthresh_swrs = nept.Epoch([], [])

                passthresh_tuningcurves = getattr(true_session, task_label).tuning_curves

                tasktime = getattr(passthresh_session, task_label)
                tasktime.likelihoods = passthresh_likelihoods
                tasktime.swrs = passthresh_swrs
                tasktime.tuning_curves = passthresh_tuningcurves

            passthresh_sessions.append(passthresh_session)

            passthresh_session.pickle(passthresh_path)


        if plot_individual_passthresh:
            filepath = os.path.join(output_filepath, "passthresh")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            plot_summary_individual(info, passthresh_session, shuffled_session, zone_labels,
                                    task_labels, colours, filepath)

    if plot_summary:
        title = group + "_average-posterior-during-SWRs_true"
        filepath = os.path.join(output_filepath, title + ".png")
        plot_session(true_sessions, title, task_labels, zone_labels, colours, filepath)

        title = group + "_average-posterior-during-SWRs_shuffled-%03d" % n_shuffles
        filepath = os.path.join(output_filepath, title + ".png")
        plot_session(shuffled_sessions, title, task_labels, zone_labels, colours, filepath)

        title = group + "_average-posterior-during-SWRs_passthresh" + str(percentile_thresh)
        filepath = os.path.join(output_filepath, title + ".png")
        plot_session(passthresh_sessions, title, task_labels, zone_labels, colours, filepath)

        title = group + "_merged-posterior-during-SWRs_passthresh" + str(percentile_thresh) + "-counts"
        filepath = os.path.join(output_filepath, title + ".png")
        plot_counts_merged(passthresh_counts, title, task_labels, zone_labels, colours, filepath)

        title = group + "_averaged-posterior-during-SWRs_passthresh" + str(percentile_thresh) + "-counts"
        filepath = os.path.join(output_filepath, title + ".png")
        plot_counts_averaged(passthresh_counts, title, task_labels, zone_labels, colours, filepath)


def main():
    from run import (analysis_infos,
                     r063_infos, r066_infos, r067_infos, r068_infos,
                     days1234_infos, days5678_infos,
                     day1_infos, day2_infos, day3_infos, day4_infos, day5_infos, day6_infos, day7_infos, day8_infos)

    thisdir = os.getcwd()
    pickle_filepath = os.path.join(thisdir, "cache", "pickled")
    output_filepath = os.path.join(thisdir, "plots", "decoding", "sequenceless")
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    info_groups = dict()
    info_groups["All"] = analysis_infos
    info_groups["R063"] = r063_infos
    info_groups["R066"] = r066_infos
    info_groups["R067"] = r067_infos
    info_groups["R068"] = r068_infos
    info_groups["Days1234"] = days1234_infos
    info_groups["Days5678"] = days5678_infos
    info_groups["Day1"] = day1_infos
    info_groups["Day2"] = day2_infos
    info_groups["Day3"] = day3_infos
    info_groups["Day4"] = day4_infos
    info_groups["Day5"] = day5_infos
    info_groups["Day6"] = day6_infos
    info_groups["Day7"] = day7_infos
    info_groups["Day8"] = day8_infos

    get_decoded_swr_plots(analysis_infos,
                          group="All",
                          pickle_filepath=pickle_filepath,
                          output_filepath=output_filepath,
                          n_shuffles=100,
                          update_cache=False)

    for infos, group in zip(info_groups.values(), info_groups.keys()):
        get_decoded_swr_plots(infos, group, pickle_filepath,
                              output_filepath, update_cache=False)

if __name__ == "__main__":
    main()
