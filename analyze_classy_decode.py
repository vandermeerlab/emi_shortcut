import matplotlib.pyplot as plt
import numpy as np
import warnings
import random
import scipy
import pickle
import os
import nept

from loading_data import get_data
from analyze_tuning_curves import get_only_tuning_curves
from utils_maze import get_zones
from analyze_decode_swrs import (plot_summary_individual,
                                 plot_likelihood_overspace,
                                 plot_combined,
                                 plot_stacked_summary)

thisdir = os.getcwd()
pickle_filepath = os.path.join(thisdir, "cache", "pickled")
output_filepath = os.path.join(thisdir, "plots", "trials", "decoding", "shuffled")
if not os.path.exists(output_filepath):
    os.makedirs(output_filepath)

# Set random seeds
random.seed(0)
np.random.seed(0)


class Session:
    """A collection of LikelihoodsAtTaskTime for each session

        Parameters
        ----------
        task_times : dict of TaskTime

    """

    def __init__(self, task_labels, zones):
        for task_label in task_labels:
            setattr(self, task_label, TaskTime([], [], [], zones))

    def pickle(self, save_path):
        with open(save_path, 'wb') as fileobj:
            print("Saving " + save_path)
            pickle.dump(self, fileobj)

    def n_tasktimes(self):
        return len(task_labels)


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
        if len(self.likelihoods) > 0:
            return np.nansum(self.likelihoods[:, :, self.zones[zone_label]], axis=2)
        else:
            return np.nan

    def means(self, zone_label):
        if len(self.likelihoods) > 0:
            return np.nanmean(self.likelihoods[:, :, self.zones[zone_label]], axis=2)
        else:
            return np.nan

    def maxs(self, zone_label):
        if len(self.likelihoods) > 0:
            return np.nanmax(self.likelihoods[:, :, self.zones[zone_label]], axis=2)
        else:
            return np.nan


def bin_spikes(spikes, time, dt, window=None, gaussian_std=None, normalized=True):
    """Bins spikes using a sliding window.

    Parameters
    ----------
    spikes: list
        Of nept.SpikeTrain
    time: np.array
    window: float or None
        Length of the sliding window, in seconds. If None, will default to dt.
    dt: float
    gaussian_std: float or None
    normalized: boolean

    Returns
    -------
    binned_spikes: nept.AnalogSignal

    """
    if window is None:
        window = dt

    bin_edges = time

    given_n_bins = window / dt
    n_bins = int(round(given_n_bins))
    if abs(n_bins - given_n_bins) > 0.01:
        warnings.warn("dt does not divide window evenly. "
                      "Using window %g instead." % (n_bins*dt))

    if normalized:
        square_filter = np.ones(n_bins) * (1 / n_bins)
    else:
        square_filter = np.ones(n_bins)

    counts = np.zeros((len(spikes), len(bin_edges) - 1))
    for idx, spiketrain in enumerate(spikes):
        counts[idx] = np.convolve(np.histogram(spiketrain.time, bins=bin_edges)[0].astype(float),
                                  square_filter, mode="same")

    if gaussian_std is not None:
        counts = nept.gaussian_filter(counts, gaussian_std, dt=dt, normalized=normalized, axis=1)

    return nept.AnalogSignal(counts, bin_edges[:-1])


def get_likelihoods(info, swr_params, task_labels, zone_labels, n_shuffles=0, save_path=None):

    _, position, spikes, lfp, _ = get_data(info)

    zones = dict()
    zones["u"], zones["shortcut"], zones["novel"] = get_zones(info, position, subset=True)
    combined_zones = zones["u"] + zones["shortcut"] + zones["novel"]
    zones["other"] = ~combined_zones

    session = Session(task_labels, zones)

    tuning_curves_fromdata = get_only_tuning_curves(info, position, spikes, info.task_times["phase3"])

    tc_shape = tuning_curves_fromdata.shape

    swrs = nept.detect_swr_hilbert(lfp,
                                   fs=info.fs,
                                   thresh=swr_params["swr_thresh"],
                                   z_thresh=swr_params["z_thresh"],
                                   power_thresh=swr_params["power_thresh"],
                                   merge_thresh=swr_params["merge_thresh"],
                                   min_length=swr_params["min_length"])
    swrs = nept.find_multi_in_epochs(spikes, swrs, min_involved=swr_params["min_involved"])

    rest_epochs = nept.rest_threshold(position, thresh=12., t_smooth=0.8)

    if n_shuffles > 0:
        n_passes = n_shuffles
    else:
        n_passes = 1

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

            for n_timebin, (start, stop) in enumerate(zip(phase_swrs.starts,
                                                          phase_swrs.stops)):
                t_window = stop-start  # 0.1 for running, 0.025 for swr

                sliced_spikes = [spiketrain.time_slice(start, stop) for spiketrain in spikes]

                counts = bin_spikes(sliced_spikes, np.array([start, stop]), dt=t_window, window=t_window,
                                    gaussian_std=0.0075, normalized=False)

                likelihood = nept.bayesian_prob(counts, tuning_curves, binsize=t_window,
                                                min_neurons=3, min_spikes=1)

                phase_likelihoods[n_pass, n_timebin] = likelihood.reshape(tc_shape[1], tc_shape[2])

        tasktime = getattr(session, task_label)
        tasktime.likelihoods = phase_likelihoods
        tasktime.tuning_curves = phase_tuningcurves
        tasktime.swrs = phase_swrs

    if save_path is not None:
        session.pickle(save_path)

    return session


if __name__ == "__main__":

    import info.r063d2 as r063d2
    import info.r068d8 as r068d8
    infos = [r068d8, r063d2]
    group = "test"

    plot_individual = False
    update_cache = True
    dont_save_pickle = False

    n_shuffles = 2
    percentile_thresh = 99

    colours = dict()
    colours["u"] = "#2b8cbe"
    colours["shortcut"] = "#31a354"
    colours["novel"] = "#d95f0e"
    colours["other"] = "#bdbdbd"

    # swr params
    swr_params = dict()
    swr_params["z_thresh"] = 2.0
    swr_params["power_thresh"] = 3.0
    swr_params["merge_thresh"] = 0.02
    swr_params["min_length"] = 0.05
    swr_params["swr_thresh"] = (140.0, 250.0)
    swr_params["min_involved"] = 4

    task_labels = ["prerecord", "pauseA", "pauseB", "postrecord"]
    zone_labels = ["u", "shortcut", "novel", "other"]

    n_sessions=len(infos)

    n_sessions = len(infos)
    all_true = []
    all_shuffled = []
    all_proportion = []
    all_passthresh = []
    all_compareshuffle = []

    for info in infos:
        print(info.session_id)

        # Get true data
        true_path = os.path.join(pickle_filepath, info.session_id+"_likelihoods_true.pkl")

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
                                           zone_labels,
                                           save_path=true_path)

        # Get shuffled data
        shuffled_path = os.path.join(pickle_filepath,
                                     info.session_id+"_likelihoods_shuffled-%03d.pkl" % n_shuffles)

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
                                               zone_labels,
                                               n_shuffles=n_shuffles,
                                               save_path=shuffled_path)


        # TODO got here
        compareshuffle = {task_time: {trajectory: 0 for trajectory in zone_labels} for task_time in task_labels}
        percentiles = {task_time: {trajectory: [] for trajectory in zone_labels} for task_time in task_labels}
        passedshuffthresh = {task_time: {trajectory: [] for trajectory in zone_labels} for task_time in task_labels}

        keep_idx = {task_time: [] for task_time in task_labels}

        for task_label in task_labels:
            raw_likelihoods_shuffs[task_label] = np.swapaxes(raw_likelihoods_shuffs[task_label], 0, 1)
            for trajectory in zone_labels:
                for idx, event in enumerate(range(len(session_sums_true[task_time][trajectory]))):
                    percentile = scipy.stats.percentileofscore(np.sort(np.array(combined_likelihoods_shuff[task_time][trajectory])[:,event]),
                                                               session_sums_true[task_time][trajectory][event])
                    percentiles[task_time][trajectory].append(percentile)
                    if percentile >= percentile_thresh:
                        compareshuffle[task_time][trajectory] += 1
                        all_compareshuffle[task_time][trajectory] += 1
                        keep_idx[task_time].append(idx)

        morelikelythanshuffle_proportion = {task_time: {trajectory: [] for trajectory in zone_labels} for task_time in task_labels}
        mean_combined_likelihoods_shuff = {task_time: {trajectory: [] for trajectory in zone_labels} for task_time in task_labels}
        passedshuffthresh_n_swr = {task_time: 0 for task_time in task_labels}

        for task_time in task_labels:
            passedshuffthresh_n_swr[task_time] += len(np.unique(keep_idx[task_time]))
            all_likelihoods_true_passthresh_n_swr[task_time] += len(np.unique(keep_idx[task_time]))
            for trajectory in zone_labels:
                if len(np.sort(np.unique(keep_idx[task_time]))) > 0:
                    passedshuffthresh[task_time][trajectory].append(np.array(session_sums_true[task_time][trajectory])[np.sort(np.unique(keep_idx[task_time]))])
                if len(session_sums_true[task_time][trajectory]) > 0:
                    morelikelythanshuffle_proportion[task_time][trajectory].append(compareshuffle[task_time][trajectory] / len(session_sums_true[task_time][trajectory]))
                else:
                    morelikelythanshuffle_proportion[task_time][trajectory].append(0.0)
                mean_combined_likelihoods_shuff[task_time][trajectory] = np.nanmean(combined_likelihoods_shuff[task_time][trajectory], axis=0)

                all_likelihoods_true[task_time][trajectory].extend(session_sums_true[task_time][trajectory])
                if len(passedshuffthresh[task_time][trajectory]) > 0:
                    all_likelihoods_true_passthresh[task_time][trajectory].append(passedshuffthresh[task_time][trajectory][0])
                else:
                    all_likelihoods_true_passthresh[task_time][trajectory].append([])
                all_likelihoods_shuff[task_time][trajectory].extend(mean_combined_likelihoods_shuff[task_time][trajectory])
                all_likelihoods_proportion[task_time][trajectory].extend(morelikelythanshuffle_proportion[task_time][trajectory])

                if plot_individual:
                    # plot percentiles
                    fig, ax = plt.subplots()
                    n = np.arange(len(percentiles[task_time][trajectory]))
                    plt.bar(n, np.sort(percentiles[task_time][trajectory]), color=colours[trajectory])
                    ax.axhline(percentile_thresh, ls="--", lw=1.5, color="k")
                    title = info.session_id + " individual SWR percentile with shuffle" + str(n_shuffles) + " for " + task_time + " " + trajectory
                    plt.title(title, fontsize=11)
                    plt.tight_layout()
                    plt.savefig(os.path.join(output_filepath, "percentiles", title))
                    plt.close()

            filepath = os.path.join(output_filepath, info.session_id+"-average-likelihood-overspace_"+task_time+".png")
            if len(session_sums_true[task_time]) > 0:
                if plot_individual:
                    plot_likelihood_overspace(info, position, raw_likelihoods_true[task_time],
                                              zones, colours, filepath)

        filename = info.session_id + " proportion of SWRs above "+str(percentile_thresh)+" percentile"
        plot_combined(morelikelythanshuffle_proportion, passedshuffthresh_n_swr,
                      task_labels, zone_labels, n_sessions=1, colours=colours, filename=filename)

        filename = info.session_id + " average posteriors during SWRs_sum-shuffled"+str(n_shuffles)
        plot_combined(mean_combined_likelihoods_shuff, n_swrs, task_labels, zone_labels,
                      n_sessions=1, colours=colours, filename=filename)

        filename = info.session_id + " average posteriors during SWRs_sum-true"
        plot_combined(session_sums_true, n_swrs, task_labels, zone_labels,
                      n_sessions=1, colours=colours, filename=filename)

        filename = info.session_id + " average posteriors during SWRs_sum-true_passthresh"
        plot_combined(passedshuffthresh, n_swrs, task_labels, zone_labels,
                      n_sessions=1, colours=colours, filename=filename)

        if plot_individual:
            for task_time in task_labels:
                for idx in range(phase_swrs[task_time].n_epochs):
                    filename = info.session_id + "_" + task_time + "_summary-swr" + str(idx) + ".png"
                    filepath = os.path.join(output_filepath, "swr", filename)
                    plot_summary_individual(info, raw_likelihoods_true[task_time][idx],
                                            raw_likelihoods_shuffs[task_time][idx],
                                            position, lfp, spikes,
                                            phase_swrs[task_time].starts[idx],
                                            phase_swrs[task_time].stops[idx],
                                            zones, zone_labels, colours, filepath, savefig=True)

    n_total = {task_time: 0 for task_time in task_labels}
    for task_time in task_labels:
        for trajectory in zone_labels:
            n_total[task_time] += all_compareshuffle[task_time][trajectory]

    all_compareshuffles = {task_time: {trajectory: [] for trajectory in zone_labels} for task_time in task_labels}
    for task_time in task_labels:
        for trajectory in zone_labels:
            all_compareshuffles[task_time][trajectory].append(all_compareshuffle[task_time][trajectory] / n_total[task_time])


    for task_time in task_labels:
        for trajectory in zone_labels:
            all_likelihoods_true_passthresh[task_time][trajectory] = np.squeeze(np.hstack(all_likelihoods_true_passthresh[task_time][trajectory]))



    filename = group + " average posteriors during SWRs_sum-shuffled"+str(n_shuffles)
    plot_combined(all_likelihoods_shuff, n_all_swrs, task_labels, zone_labels,
                  n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-true"
    plot_combined(all_likelihoods_true, n_all_swrs, task_labels, zone_labels,
                  n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-true_passthresh"
    plot_combined(all_likelihoods_true_passthresh, all_likelihoods_true_passthresh_n_swr,
                  task_labels, zone_labels, n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-true_passthresh-overallproportion"
    plot_combined(all_compareshuffles, all_likelihoods_true_passthresh_n_swr,
                  task_labels, zone_labels, n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + "average posteriors during SWRs_sum-stacked-shuffled"+str(n_shuffles)
    plot_stacked_summary(all_likelihoods_shuff, n_all_swrs, task_labels, zone_labels,
                         n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-stacked-true"
    plot_stacked_summary(all_likelihoods_true, n_all_swrs, task_labels, zone_labels,
                         n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-stacked-true_passthresh"
    plot_stacked_summary(all_likelihoods_true_passthresh, n_all_swrs, task_labels,
                         zone_labels, n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " proportion of SWRs above the "+str(percentile_thresh)+" percentile (shuffle" + str(n_shuffles) + ")"
    plot_combined(all_likelihoods_proportion, n_all_swrs, task_labels, zone_labels,
                  n_sessions=len(infos), colours=colours, filename=filename)
