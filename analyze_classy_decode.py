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


class Likelihoods:
    """A collection of LikelihoodsAtTaskTime for each session

        Parameters
        ----------
        task_times : dict of TaskTime

    """

    def __init__(self, task_times):
        self.task_times = task_times


class TaskTime:
    """A set of decoded likelihoods for a given task time

        Parameters
        ----------
        likelihoods : np.array
            With shape (ntimebins, nxbins, nybins)

        Attributes
        ----------
        likelihoods : np.array
            With shape (ntimebins, nxbins, nybins)

    """

    def __init__(self, likelihoods):
        self.likelihoods = likelihoods

    def sum(self, zone):
        return np.nansum(self.likelihoods[zone])

    def mean(self, zone):
        return np.nanmean(self.likelihoods[zone])

    def max(self, zone):
        return np.nanmax(self.likelihoods[zone])


class Zones:
    """A set of decoded likelihoods for a given task time

            Parameters
            ----------
            likelihoods : np.array
                With shape (ntimebins, nxbins, nybins)

            Attributes
            ----------
            likelihoods : np.array
                With shape (ntimebins, nxbins, nybins)

        """

    def __init__(self, zones):
        self.zones = zones


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


def raw_likelihood(spikes, tuning_curves, tc_shape, start, stop):
    sliced_spikes = [spiketrain.time_slice(start, stop) for spiketrain in spikes]
    t_window = stop-start  # 0.1 for running, 0.025 for swr
    counts = bin_spikes(sliced_spikes, np.array([start, stop]), dt=t_window, window=t_window,
                        gaussian_std=0.0075, normalized=False)
    likelihood = nept.bayesian_prob(counts, tuning_curves, binsize=t_window, min_neurons=3, min_spikes=1)

    return likelihood.reshape(tc_shape[1], tc_shape[2])


def get_likelihoods(tuning_curves_fromdata, tc_shape, spikes, phase_swrs,
                    zones, task_times, maze_segments, shuffled_id=False):

    if shuffled_id:
        tuning_curves = np.random.permutation(tuning_curves_fromdata)
    else:
        tuning_curves = tuning_curves_fromdata

    tuning_curves = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

    # likelihoods_sum = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    # raw_likelihoods = {task_time: [] for task_time in task_times}

    for i, task_time in enumerate(task_times):
        likelihoods = np.zeros(len(phase_swrs[task_time].n_epochs))
        for j, (start, stop) in enumerate(zip(phase_swrs[task_time].starts, phase_swrs[task_time].stops)):
            likelihoods[j] = raw_likelihood(spikes, tuning_curves, tc_shape, start, stop)
        huh = TaskTime(likelihoods)
    return likelihoods_sum, raw_likelihoods


def pickle_likelihoods(tuning_curves_fromdata, tc_shape, spikes, phase_swrs, zones, task_times, maze_segments,
                       shuffled_id, raw_path, sum_path):

    likelihoods_sum, raw_likelihoods = get_likelihoods(tuning_curves_fromdata,
                                                       tc_shape,
                                                       spikes,
                                                       phase_swrs,
                                                       zones,
                                                       task_times,
                                                       maze_segments,
                                                       shuffled_id)
    with open(sum_path, 'wb') as fileobj:
        pickle.dump(likelihoods_sum, fileobj)

    with open(raw_path, 'wb') as fileobj:
        pickle.dump(raw_likelihoods, fileobj)

    return likelihoods_sum, raw_likelihoods


def save_likelihoods(info, position, spikes, phase_swrs, zones, task_times, maze_segments, n_shuffles):
    tuning_curves_fromdata = get_only_tuning_curves(info,
                                           position,
                                           spikes,
                                           info.task_times["phase3"])

    tc_shape = tuning_curves_fromdata.shape

    raw_path_true = os.path.join(pickle_filepath, info.session_id+"_raw-likelihoods_true.pkl")
    sum_path_true = os.path.join(pickle_filepath, info.session_id+"_sum-likelihoods_true.pkl")

    session_likelihoods_true, raw_likelihoods_true = pickle_likelihoods(tuning_curves_fromdata,
                                                                        tc_shape,
                                                                        spikes,
                                                                        phase_swrs,
                                                                        zones,
                                                                        task_times,
                                                                        maze_segments,
                                                                        shuffled_id=False,
                                                                        raw_path=raw_path_true,
                                                                        sum_path=sum_path_true)

    combined_likelihoods_shuff = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    raw_likelihoods_shuffs = {task_time: [] for task_time in task_times}

    for i_shuffle in range(n_shuffles):
        raw_path_shuff = os.path.join(pickle_filepath,
                                      info.session_id+"_raw-likelihoods_shuffled-%03d.pkl" % i_shuffle)
        sum_path_shuff = os.path.join(pickle_filepath,
                                      info.session_id+"_sum-likelihoods_shuffled-%03d.pkl" % i_shuffle)


        session_likelihoods_shuff, raw_likelihoods_shuff = pickle_likelihoods(tuning_curves_fromdata,
                                                                              tc_shape,
                                                                              spikes,
                                                                              phase_swrs,
                                                                              zones,
                                                                              task_times,
                                                                              maze_segments,
                                                                              shuffled_id=True,
                                                                              raw_path=raw_path_shuff,
                                                                              sum_path=sum_path_shuff)

        for task_time in task_times:
            raw_likelihoods_shuffs[task_time].append(raw_likelihoods_shuff[task_time])
            for trajectory in maze_segments:
                combined_likelihoods_shuff[task_time][trajectory].append(np.array(session_likelihoods_shuff[task_time][trajectory]))
    return true_likelihoods, shuffled_likelihoods


if __name__ == "__main__":

    import info.r063d2 as r063d2
    import info.r068d8 as r068d8
    infos = [r068d8, r063d2]
    group = "test"

    plot_individual = False
    update_cache = False

    n_shuffles = 2
    percentile_thresh = 99

    colours = dict()
    colours["u"] = "#2b8cbe"
    colours["shortcut"] = "#31a354"
    colours["novel"] = "#d95f0e"
    colours["other"] = "#bdbdbd"

    # swr params
    z_thresh = 2.0
    power_thresh = 3.0
    merge_thresh = 0.02
    min_length = 0.05
    swr_thresh = (140.0, 250.0)

    task_times = ["prerecord", "pauseA", "pauseB", "postrecord"]
    maze_segments = ["u", "shortcut", "novel", "other"]

    n_sessions = len(infos)
    all_true = []
    all_shuffled = []
    all_proportion = []
    all_passthresh = []
    all_compareshuffle = []

    for info in infos:
        print(info.session_id)

        events, position, spikes, lfp, _ = get_data(info)

        # Define zones
        zones = dict()
        zones["u"], zones["shortcut"], zones["novel"] = get_zones(info, position, subset=True)
        combined_zones = zones["u"] + zones["shortcut"] + zones["novel"]
        zones["other"] = ~combined_zones

        # Find SWRs for the whole session
        swrs_path = os.path.join(pickle_filepath, info.session_id+"_swrs.pkl")

        # Remove previous pickle if update_cache
        if update_cache:
            if os.path.exists(swrs_path):
                os.remove(swrs_path)

        # Load pickle if it exists, otherwise compute and pickle
        if os.path.exists(swrs_path):
            print("Loading pickled true likelihoods...")
            with open(swrs_path, 'rb') as fileobj:
                swrs = pickle.load(fileobj)
        else:
            swrs = nept.detect_swr_hilbert(lfp, fs=info.fs, thresh=swr_thresh, z_thresh=z_thresh,
                                           power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)
            swrs = nept.find_multi_in_epochs(spikes, swrs, min_involved=4)

        rest_epochs = nept.rest_threshold(position, thresh=12., t_smooth=0.8)

        # Restrict SWRs to those during epochs of interest during rest
        phase_swrs = dict()

        for task_time in task_times:
            epochs_of_interest = info.task_times[task_time].intersect(rest_epochs)

            phase_swrs[task_time] = epochs_of_interest.overlaps(swrs)
            phase_swrs[task_time] = phase_swrs[task_time][phase_swrs[task_time].durations >= 0.05]

        true_likelihoods_path = os.path.join(pickle_filepath, info.session_id+"_likelihoods_true.pkl")

        # Remove previous pickle if update_cache
        if update_cache:
            if os.path.exists(true_likelihoods_path):
                os.remove(true_likelihoods_path)

        # Load pickle if it exists, otherwise compute and pickle
        if os.path.exists(true_likelihoods_path):
            print("Loading pickled true likelihoods...")
            compute_likelihoods = False
            with open(true_likelihoods_path, 'rb') as fileobj:
                true_likelihoods = pickle.load(fileobj)
        else:
            compute_likelihoods = True

        shuffled_likelihoods = []

        for i_shuffle in range(n_shuffles):
            shuffled_likelihoods_path = os.path.join(pickle_filepath,
                                                     info.session_id+"_likelihoods_shuffled-%03d.pkl" % i_shuffle)

            # Remove previous pickle if update_cache
            if update_cache:
                if os.path.exists(shuffled_likelihoods_path):
                    os.remove(shuffled_likelihoods_path)

            # Load pickle if it exists, otherwise compute and pickle
            if os.path.exists(shuffled_likelihoods_path):
                print("Loading pickled shuffled likelihoods "+str(i_shuffle)+"...")
                with open(shuffled_likelihoods_path, 'rb') as fileobj:
                    single_shuffled_likelihoods = pickle.load(fileobj)
            else:
                compute_likelihoods = True
                break

            shuffled_likelihoods.append(single_shuffled_likelihoods)

        if compute_likelihoods:
            true_likelihoods, shuffled_likelihoods = save_likelihoods(info,
                                                                      position,
                                                                      spikes,
                                                                      phase_swrs,
                                                                      zones,
                                                                      task_times,
                                                                      maze_segments,
                                                                      n_shuffles)

        compareshuffle = {task_time: {trajectory: 0 for trajectory in maze_segments} for task_time in task_times}
        percentiles = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
        passedshuffthresh = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}

        keep_idx = {task_time: [] for task_time in task_times}

        for task_time in task_times:
            raw_likelihoods_shuffs[task_time] = np.swapaxes(raw_likelihoods_shuffs[task_time], 0, 1)
            for trajectory in maze_segments:
                for idx, event in enumerate(range(len(session_sums_true[task_time][trajectory]))):
                    percentile = scipy.stats.percentileofscore(np.sort(np.array(combined_likelihoods_shuff[task_time][trajectory])[:,event]),
                                                               session_sums_true[task_time][trajectory][event])
                    percentiles[task_time][trajectory].append(percentile)
                    if percentile >= percentile_thresh:
                        compareshuffle[task_time][trajectory] += 1
                        all_compareshuffle[task_time][trajectory] += 1
                        keep_idx[task_time].append(idx)

        morelikelythanshuffle_proportion = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
        mean_combined_likelihoods_shuff = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
        passedshuffthresh_n_swr = {task_time: 0 for task_time in task_times}

        for task_time in task_times:
            passedshuffthresh_n_swr[task_time] += len(np.unique(keep_idx[task_time]))
            all_likelihoods_true_passthresh_n_swr[task_time] += len(np.unique(keep_idx[task_time]))
            for trajectory in maze_segments:
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
                      task_times, maze_segments, n_sessions=1, colours=colours, filename=filename)

        filename = info.session_id + " average posteriors during SWRs_sum-shuffled"+str(n_shuffles)
        plot_combined(mean_combined_likelihoods_shuff, n_swrs, task_times, maze_segments,
                      n_sessions=1, colours=colours, filename=filename)

        filename = info.session_id + " average posteriors during SWRs_sum-true"
        plot_combined(session_sums_true, n_swrs, task_times, maze_segments,
                      n_sessions=1, colours=colours, filename=filename)

        filename = info.session_id + " average posteriors during SWRs_sum-true_passthresh"
        plot_combined(passedshuffthresh, n_swrs, task_times, maze_segments,
                      n_sessions=1, colours=colours, filename=filename)

        if plot_individual:
            for task_time in task_times:
                for idx in range(phase_swrs[task_time].n_epochs):
                    filename = info.session_id + "_" + task_time + "_summary-swr" + str(idx) + ".png"
                    filepath = os.path.join(output_filepath, "swr", filename)
                    plot_summary_individual(info, raw_likelihoods_true[task_time][idx],
                                            raw_likelihoods_shuffs[task_time][idx],
                                            position, lfp, spikes,
                                            phase_swrs[task_time].starts[idx],
                                            phase_swrs[task_time].stops[idx],
                                            zones, maze_segments, colours, filepath, savefig=True)

    n_total = {task_time: 0 for task_time in task_times}
    for task_time in task_times:
        for trajectory in maze_segments:
            n_total[task_time] += all_compareshuffle[task_time][trajectory]

    all_compareshuffles = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    for task_time in task_times:
        for trajectory in maze_segments:
            all_compareshuffles[task_time][trajectory].append(all_compareshuffle[task_time][trajectory] / n_total[task_time])


    for task_time in task_times:
        for trajectory in maze_segments:
            all_likelihoods_true_passthresh[task_time][trajectory] = np.squeeze(np.hstack(all_likelihoods_true_passthresh[task_time][trajectory]))



    filename = group + " average posteriors during SWRs_sum-shuffled"+str(n_shuffles)
    plot_combined(all_likelihoods_shuff, n_all_swrs, task_times, maze_segments,
                  n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-true"
    plot_combined(all_likelihoods_true, n_all_swrs, task_times, maze_segments,
                  n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-true_passthresh"
    plot_combined(all_likelihoods_true_passthresh, all_likelihoods_true_passthresh_n_swr,
                  task_times, maze_segments, n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-true_passthresh-overallproportion"
    plot_combined(all_compareshuffles, all_likelihoods_true_passthresh_n_swr,
                  task_times, maze_segments, n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + "average posteriors during SWRs_sum-stacked-shuffled"+str(n_shuffles)
    plot_stacked_summary(all_likelihoods_shuff, n_all_swrs, task_times, maze_segments,
                         n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-stacked-true"
    plot_stacked_summary(all_likelihoods_true, n_all_swrs, task_times, maze_segments,
                         n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " average posteriors during SWRs_sum-stacked-true_passthresh"
    plot_stacked_summary(all_likelihoods_true_passthresh, n_all_swrs, task_times,
                         maze_segments, n_sessions=len(infos), colours=colours, filename=filename)

    filename = group + " proportion of SWRs above the "+str(percentile_thresh)+" percentile (shuffle" + str(n_shuffles) + ")"
    plot_combined(all_likelihoods_proportion, n_all_swrs, task_times, maze_segments,
                  n_sessions=len(infos), colours=colours, filename=filename)