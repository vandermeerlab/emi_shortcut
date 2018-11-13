import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import warnings
import numpy as np
import scipy
import pickle
import os
import scalebar
import nept
import random

from loading_data import get_data
from analyze_tuning_curves import get_only_tuning_curves
from utils_maze import get_zones, get_bin_centers

thisdir = os.getcwd()
pickle_filepath = os.path.join(thisdir, "cache", "pickled")
output_filepath = os.path.join(thisdir, "plots", "trials", "decoding", "shuffled")
if not os.path.exists(output_filepath):
    os.makedirs(output_filepath)

# Set random seeds
random.seed(0)
np.random.seed(0)


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


def plot_summary_individual(info, likelihood_true, likelihood_shuff, position, lfp, spikes, start, stop,
                            zones, maze_segments, colours, filepath=None, savefig=False):
    buffer = 0.1

    means = [np.nansum(likelihood_true[zones[trajectory]]) for trajectory in maze_segments]

    means_shuff = [np.nanmean(np.nansum(likelihood_shuff[:, zones[trajectory]], axis=1)) for trajectory in maze_segments]
    sems_shuff = [scipy.stats.sem(np.nansum(likelihood_shuff[:, zones[trajectory]], axis=1), nan_policy="omit") for trajectory in maze_segments]

    sliced_spikes = [spiketrain.time_slice(start-buffer, stop+buffer) for spiketrain in spikes]

    rows = len(sliced_spikes)
    add_rows = int(rows / 8)

    ms = 600 / rows
    mew = 0.7
    spike_loc = 1

    fig = plt.figure(figsize=(8, 8))
    gs1 = gridspec.GridSpec(3, 2)
    gs1.update(wspace=0.3, hspace=0.3)

    ax1 = plt.subplot(gs1[1:, 0])
    for idx, neuron_spikes in enumerate(sliced_spikes):
        ax1.plot(neuron_spikes.time, np.ones(len(neuron_spikes.time)) + (idx * spike_loc), '|',
                 color='k', ms=ms, mew=mew)
    ax1.axis('off')

    ax2 = plt.subplot(gs1[0, 0], sharex=ax1)

    swr_highlight = "#fc4e2a"
    start_idx = nept.find_nearest_idx(lfp.time, start - buffer)
    stop_idx = nept.find_nearest_idx(lfp.time, stop + buffer)
    ax2.plot(lfp.time[start_idx:stop_idx], lfp.data[start_idx:stop_idx], color="k", lw=0.3, alpha=0.9)

    start_idx = nept.find_nearest_idx(lfp.time, start)
    stop_idx = nept.find_nearest_idx(lfp.time, stop)
    ax2.plot(lfp.time[start_idx:stop_idx], lfp.data[start_idx:stop_idx], color=swr_highlight, lw=0.6)
    ax2.axis("off")

    ax1.axvline(lfp.time[start_idx], linewidth=1, color=swr_highlight)
    ax1.axvline(lfp.time[stop_idx], linewidth=1, color=swr_highlight)
    ax1.axvspan(lfp.time[start_idx], lfp.time[stop_idx], alpha=0.2, color=swr_highlight)

    scalebar.add_scalebar(ax2, matchy=False, bbox_transform=fig.transFigure,
                          bbox_to_anchor=(0.25, 0.05), units='ms')

    likelihood_true[np.isnan(likelihood_true)] = 0

    xx, yy = np.meshgrid(info.xedges, info.yedges)
    xcenters, ycenters = get_bin_centers(info)
    xxx, yyy = np.meshgrid(xcenters, ycenters)

    maze_highlight = "#fed976"
    ax3 = plt.subplot(gs1[0, 1])
    sliced_position = position.time_slice(info.task_times["phase3"].starts, info.task_times["phase3"].stops)
    ax3.plot(sliced_position.x, sliced_position.y, ".", color=maze_highlight, ms=1, alpha=0.2)
    pp = ax3.pcolormesh(xx, yy, likelihood_true, cmap='bone_r')
    ax3.contour(xxx, yyy, zones["u"], levels=0, colors=colours["u"])
    ax3.contour(xxx, yyy, zones["shortcut"], levels=0, colors=colours["shortcut"])
    ax3.contour(xxx, yyy, zones["novel"], levels=0, colors=colours["novel"])
    plt.colorbar(pp)
    ax3.axis('off')

    ax4 = plt.subplot(gs1[1:2, 1])
    n = np.arange(len(maze_segments))
    ax4.bar(n, means,
            color=[colours["u"], colours["shortcut"], colours["novel"], colours["other"]], edgecolor='k')
    ax4.set_xticks(n)
    ax4.set_xticklabels([], rotation=90)
    ax4.set_ylim([0, 1.])
    ax4.set_title("True proportion", fontsize=14)

    ax5 = plt.subplot(gs1[2:, 1], sharey=ax4)
    n = np.arange(len(maze_segments))
    ax5.bar(n, means_shuff,
            yerr=sems_shuff,
            color=[colours["u"], colours["shortcut"], colours["novel"], colours["other"]], edgecolor='k')
    ax5.set_xticks(n)
    ax5.set_xticklabels(maze_segments, rotation=90)
    ax5.set_ylim([0, 1.])
    ax5.set_title("Shuffled proportion", fontsize=14)

    plt.tight_layout()

    if savefig:
        plt.savefig(filepath)
        plt.close()
    else:
        plt.show()


def plot_likelihood_overspace(info, position, likelihoods, zones, colours, filepath=None):

    xx, yy = np.meshgrid(info.xedges, info.yedges)
    xcenters, ycenters = get_bin_centers(info)
    xxx, yyy = np.meshgrid(xcenters, ycenters)

    sliced_position = position.time_slice(info.task_times["phase3"].starts, info.task_times["phase3"].stops)
    plt.plot(sliced_position.x, sliced_position.y, "b.", ms=1, alpha=0.2)
    pp = plt.pcolormesh(xx, yy, np.nanmean(likelihoods, axis=0), vmax=0.2, cmap='bone_r')
    plt.contour(xxx, yyy, zones["u"], levels=0, colors=colours["u"], corner_mask=False)
    plt.contour(xxx, yyy, zones["shortcut"], levels=0, colors=colours["shortcut"], corner_mask=False)
    plt.contour(xxx, yyy, zones["novel"], levels=0, colors=colours["novel"], corner_mask=False)

    plt.colorbar(pp)
    plt.axis('off')
    if filepath is not None:
        plt.savefig(filepath)
        plt.close()
    else:
        plt.show()


def get_likelihood(spikes, tuning_curves, tc_shape, start, stop):
    sliced_spikes = [spiketrain.time_slice(start, stop) for spiketrain in spikes]
    t_window = stop-start  # 0.1 for running, 0.025 for swr
    counts = bin_spikes(sliced_spikes, np.array([start, stop]), dt=t_window, window=t_window,
                        gaussian_std=0.0075, normalized=False)
    likelihood = nept.bayesian_prob(counts, tuning_curves, binsize=t_window, min_neurons=3, min_spikes=1)

    return likelihood.reshape(tc_shape[1], tc_shape[2])


def plot_combined(summary_likelihoods, n_all_swrs, task_times, maze_segments, n_sessions, colours, filename=None):

    trajectory_means = {key: [] for key in maze_segments}
    trajectory_sems = {key: [] for key in maze_segments}

    for trajectory in maze_segments:
        trajectory_means[trajectory] = [np.nanmean(summary_likelihoods[task_time][trajectory])
                                        if len(summary_likelihoods[task_time][trajectory]) > 0 else 0.0
                                        for task_time in task_times]

        trajectory_sems[trajectory] = [scipy.stats.sem(summary_likelihoods[task_time][trajectory], nan_policy="omit")
                                       if len(summary_likelihoods[task_time][trajectory]) > 1 else 0.0
                                       for task_time in task_times]

    fig = plt.figure(figsize=(12, 6))
    gs1 = gridspec.GridSpec(1, 4)
    gs1.update(wspace=0.3, hspace=0.)

    n = np.arange(len(task_times))
    ax1 = plt.subplot(gs1[0])
    ax1.bar(n, trajectory_means["u"], yerr=trajectory_sems["u"], color=colours["u"])
    ax2 = plt.subplot(gs1[1])
    ax2.bar(n, trajectory_means["shortcut"], yerr=trajectory_sems["shortcut"], color=colours["shortcut"])
    ax3 = plt.subplot(gs1[2])
    ax3.bar(n, trajectory_means["novel"], yerr=trajectory_sems["novel"], color=colours["novel"])
    ax4 = plt.subplot(gs1[3])
    ax4.bar(n, trajectory_means["other"], yerr=trajectory_sems["other"], color=colours["other"])

    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_ylim([0, 1.])

        ax.set_xticks(np.arange(len(task_times)))
        ax.set_xticklabels(task_times, rotation = 90)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        for i, task_time in enumerate(task_times):
            ax.text(i, 0.01, str(n_all_swrs[task_time]), ha="center", fontsize=14)

    for ax in [ax2, ax3, ax4]:
        ax.set_yticklabels([])

    plt.text(1., 1., "n sessions: "+ str(n_sessions), horizontalalignment='left',
             verticalalignment='top', fontsize=14)

    fig.suptitle(filename, fontsize=18)
#     ax1.set_ylabel("Proportion")

    legend_elements = [Patch(facecolor=colours["u"], edgecolor='k', label="u"),
                       Patch(facecolor=colours["shortcut"], edgecolor='k', label="shortcut"),
                       Patch(facecolor=colours["novel"], edgecolor='k', label="novel"),
                       Patch(facecolor=colours["other"], edgecolor='k', label="other")]
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1.0))

    gs1.tight_layout(fig)

    if filename is not None:
        plt.savefig(os.path.join(output_filepath, filename+".png"))
        plt.close()
    else:
        plt.show()


def plot_stacked_summary(summary_likelihoods, n_all_swrs, task_times,
                         maze_segments, n_sessions, colours, filename=None):

    trajectory_means = {key: [] for key in maze_segments}
    trajectory_sems = {key: [] for key in maze_segments}

    for trajectory in maze_segments:
        trajectory_means[trajectory] = [np.nanmean(summary_likelihoods[task_time][trajectory])
                                        for task_time in task_times]
        trajectory_sems[trajectory] = [scipy.stats.sem(summary_likelihoods[task_time][trajectory])
                                       for task_time in task_times]

    fig, ax = plt.subplots(figsize=(7,5))
    n = np.arange(len(task_times))
    pu = plt.bar(n, trajectory_means["u"], yerr=trajectory_sems["u"], color=colours["u"])
    ps = plt.bar(n, trajectory_means["shortcut"], yerr=trajectory_sems["shortcut"],
                 bottom=trajectory_means["u"], color=colours["shortcut"])
    pn = plt.bar(n, trajectory_means["novel"], yerr=trajectory_sems["novel"],
                 bottom=np.array(trajectory_means["u"])+np.array(trajectory_means["shortcut"]), color=colours["novel"])
    po = plt.bar(n, trajectory_means["other"], yerr=trajectory_sems["other"],
                 bottom=np.array(trajectory_means["u"])+np.array(trajectory_means["shortcut"])+np.array(trajectory_means["novel"]),
                 color=colours["other"])
    plt.xticks(n, task_times)
    plt.title(filename)

    for i, task_time in enumerate(task_times):
        ax.text(i, 0.01, str(n_all_swrs[task_time]), ha="center", fontsize=14)

    plt.text(2.8, -0.15, "n sessions: "+ str(n_sessions), fontsize=14)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.tight_layout()
    if filename is not None:
        plt.savefig(os.path.join(output_filepath, filename+".png"))
        plt.close()
    else:
        plt.show()


def get_likelihoods(tuning_curves_fromdata, tc_shape, spikes, phase_swrs, zones, task_times, maze_segments, shuffled_id=False):

    if shuffled_id:
        tuning_curves = np.random.permutation(tuning_curves_fromdata)
    else:
        tuning_curves = tuning_curves_fromdata

    tuning_curves = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

    likelihoods_sum = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    raw_likelihoods = {task_time: [] for task_time in task_times}

    for i, task_time in enumerate(task_times):
        for (start, stop) in zip(phase_swrs[task_time].starts, phase_swrs[task_time].stops):
            likelihood = get_likelihood(spikes, tuning_curves, tc_shape, start, stop)
            raw_likelihoods[task_time].append(likelihood)

            for trajectory in maze_segments:
                likelihoods_sum[task_time][trajectory].append(np.nansum(likelihood[zones[trajectory]]))

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
    return session_likelihoods_true, raw_likelihoods_true, combined_likelihoods_shuff, raw_likelihoods_shuffs


def get_decoded_swr_plots(infos, group, z_thresh=2., power_thresh=3., update_cache=True):
    plot_individual = True

    n_shuffles = 100
    percentile_thresh = 99

    colours = dict()
    colours["u"] = "#2b8cbe"
    colours["shortcut"] = "#31a354"
    colours["novel"] = "#d95f0e"
    colours["other"] = "#bdbdbd"

    # swr params
    merge_thresh = 0.02
    min_length = 0.05
    swr_thresh = (140.0, 250.0)

    task_times = ["prerecord", "pauseA", "pauseB", "postrecord"]
    maze_segments = ["u", "shortcut", "novel", "other"]

    n_sessions = len(infos)
    all_likelihoods_true = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    all_likelihoods_shuff = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    all_likelihoods_proportion = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    all_likelihoods_true_passthresh = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
    all_likelihoods_true_passthresh_n_swr = {task_time: 0 for task_time in task_times}
    all_compareshuffle = {task_time: {trajectory: 0 for trajectory in maze_segments} for task_time in task_times}

    n_all_swrs = {task_time: 0 for task_time in task_times}

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
        n_swrs = {task_time: 0 for task_time in task_times}

        for task_time in task_times:
            epochs_of_interest = info.task_times[task_time].intersect(rest_epochs)

            phase_swrs[task_time] = epochs_of_interest.overlaps(swrs)
            phase_swrs[task_time] = phase_swrs[task_time][phase_swrs[task_time].durations >= 0.05]

            n_swrs[task_time] += phase_swrs[task_time].n_epochs
            n_all_swrs[task_time] += phase_swrs[task_time].n_epochs

        raw_path_true = os.path.join(pickle_filepath, info.session_id+"_raw-likelihoods_true.pkl")
        sum_path_true = os.path.join(pickle_filepath, info.session_id+"_sum-likelihoods_true.pkl")

        # Remove previous pickle if update_cache
        if update_cache:
            if os.path.exists(raw_path_true):
                os.remove(raw_path_true)
            if os.path.exists(sum_path_true):
                os.remove(sum_path_true)

        compute_likelihoods = False

        # Load pickle if it exists, otherwise compute and pickle
        if os.path.exists(raw_path_true) and os.path.exists(sum_path_true):
            print("Loading pickled true likelihoods...")
            with open(raw_path_true, 'rb') as fileobj:
                raw_likelihoods_true = pickle.load(fileobj)
            with open(sum_path_true, 'rb') as fileobj:
                session_sums_true = pickle.load(fileobj)

        combined_likelihoods_shuff = {task_time: {trajectory: [] for trajectory in maze_segments} for task_time in task_times}
        raw_likelihoods_shuffs = {task_time: [] for task_time in task_times}

        for i_shuffle in range(n_shuffles):
            raw_path_shuff = os.path.join(pickle_filepath,
                                          info.session_id+"_raw-likelihoods_shuffled-%03d.pkl" % i_shuffle)
            sum_path_shuff = os.path.join(pickle_filepath,
                                          info.session_id+"_sum-likelihoods_shuffled-%03d.pkl" % i_shuffle)

            # Remove previous pickle if update_cache
            if update_cache:
                if os.path.exists(raw_path_shuff):
                    os.remove(raw_path_shuff)
                if os.path.exists(sum_path_shuff):
                    os.remove(sum_path_shuff)

            # Load pickle if it exists, otherwise compute and pickle
            if os.path.exists(raw_path_shuff) and os.path.exists(sum_path_shuff):
                print("Loading pickled shuffled likelihoods "+str(i_shuffle)+"...")
                with open(raw_path_shuff, 'rb') as fileobj:
                    raw_likelihoods_shuff = pickle.load(fileobj)
                with open(sum_path_shuff, 'rb') as fileobj:
                    session_sums_shuff = pickle.load(fileobj)
            else:
                compute_likelihoods = True
                break

            for task_time in task_times:
                raw_likelihoods_shuffs[task_time].append(raw_likelihoods_shuff[task_time])
                for trajectory in maze_segments:
                    combined_likelihoods_shuff[task_time][trajectory].append(np.array(session_sums_shuff[task_time][trajectory]))
        else:
            compute_likelihoods = True

        if compute_likelihoods:
            session_sums_true, raw_likelihoods_true, combined_likelihoods_shuff, raw_likelihoods_shuffs = save_likelihoods(info, position, spikes, phase_swrs, zones, task_times, maze_segments, n_shuffles)

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
                    if len(raw_likelihoods_true[task_time]) > 0:
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


if __name__ == "__main__":

    from run import (analysis_infos,
                     r063_infos, r066_infos, r067_infos, r068_infos,
                     days1234_infos, days5678_infos,
                     day1_infos, day2_infos, day3_infos, day4_infos, day5_infos, day6_infos, day7_infos, day8_infos)

    get_decoded_swr_plots(analysis_infos, "All")
    get_decoded_swr_plots(r063_infos, "R063")
    get_decoded_swr_plots(r066_infos, "R066")
    get_decoded_swr_plots(r067_infos, "R067")
    get_decoded_swr_plots(r068_infos, "R068")
    get_decoded_swr_plots(days1234_infos, "Days1234")
    get_decoded_swr_plots(days5678_infos, "Days5678")
    get_decoded_swr_plots(day1_infos, "Day1")
    get_decoded_swr_plots(day2_infos, "Day2")
    get_decoded_swr_plots(day3_infos, "Day3")
    get_decoded_swr_plots(day4_infos, "Day4")
    get_decoded_swr_plots(day5_infos, "Day5")
    get_decoded_swr_plots(day6_infos, "Day6")
    get_decoded_swr_plots(day7_infos, "Day7")
    get_decoded_swr_plots(day8_infos, "Day8")
