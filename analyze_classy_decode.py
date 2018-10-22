import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import numpy as np
import warnings
import random
import scipy
import pickle
import os
import nept
import scalebar

from loading_data import get_data
from analyze_tuning_curves import get_only_tuning_curves
from utils_maze import get_zones
from utils_maze import get_bin_centers

thisdir = os.getcwd()
pickle_filepath = os.path.join(thisdir, "cache", "pickled")
output_filepath = os.path.join(thisdir, "plots", "trials", "decoding", "classy")
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

    session = Session(position, task_labels, zones)

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

            phase_tuningcurves[n_pass,] = tuning_curves
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

                    these_counts = bin_spikes(sliced_spikes, np.array([start, stop]), dt=t_window, window=t_window,
                                              gaussian_std=0.0075, normalized=False)

                    counts_data.append(these_counts.data)
                    counts_time.append(these_counts.time)
                    t_windows.append(t_window)

                counts = nept.AnalogSignal(np.vstack(counts_data), np.hstack(counts_time))
                likelihood = nept.bayesian_prob(counts, tuning_curves, binsize=t_windows,
                                                min_neurons=3, min_spikes=1)

                phase_likelihoods[n_pass] = likelihood.reshape(phase_swrs.n_epochs, tc_shape[1], tc_shape[2])

        tasktime = getattr(session, task_label)
        tasktime.likelihoods = phase_likelihoods
        tasktime.tuning_curves = phase_tuningcurves
        tasktime.swrs = phase_swrs

    if save_path is not None:
        session.pickle(save_path)

    return session


def plot_likelihood_overspace(info, session, task_labels, colours, filepath=None):
    for task_label in task_labels:
        zones = getattr(session, task_label).zones
        likelihood = np.nanmean(np.array(getattr(session, task_label).likelihoods), axis=(0, 1))

        likelihood[np.isnan(likelihood)] = 0

        xx, yy = np.meshgrid(info.xedges, info.yedges)
        xcenters, ycenters = get_bin_centers(info)
        xxx, yyy = np.meshgrid(xcenters, ycenters)

        maze_highlight = "#fed976"
        plt.plot(session.position.x, session.position.y, ".", color=maze_highlight, ms=1, alpha=0.2)
        pp = plt.pcolormesh(xx, yy, likelihood, cmap='bone_r')
        for label in ["u", "shortcut", "novel"]:
            plt.contour(xxx, yyy, zones[label], levels=0, linewidths=2, colors=colours[label])
        plt.colorbar(pp)
        plt.axis('off')

        plt.tight_layout()
        if filepath is not None:
            filename = info.session_id + "_" + task_label + "_likelihoods-overspace.png"
            plt.savefig(os.path.join(filepath, filename))
            plt.close()
        else:
            plt.show()


def plot_summary_individual(info, session_true, session_shuffled, zone_labels, task_labels, colours, filepath=None):
    _, position, spikes, lfp, _ = get_data(info)

    buffer = 0.1

    for task_label in task_labels:
        swrs = getattr(session_true, task_label).swrs
        zones = getattr(session_true, task_label).zones
        if swrs is not None:
            for swr_idx in range(swrs.n_epochs):
                start = swrs[swr_idx].start
                stop = swrs[swr_idx].stop

                sliced_spikes = [spiketrain.time_slice(start - buffer, stop + buffer) for spiketrain in spikes]

                ms = 600 / len(sliced_spikes)
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

                likelihood_true = np.array(getattr(session_true, task_label).likelihoods[:, swr_idx])

                likelihood_true[np.isnan(likelihood_true)] = 0

                xx, yy = np.meshgrid(info.xedges, info.yedges)
                xcenters, ycenters = get_bin_centers(info)
                xxx, yyy = np.meshgrid(xcenters, ycenters)

                maze_highlight = "#fed976"
                ax3 = plt.subplot(gs1[0, 1])

                ax3.plot(session_true.position.x, session_true.position.y, ".",
                         color=maze_highlight, ms=1, alpha=0.2)
                pp = ax3.pcolormesh(xx, yy, likelihood_true[0], cmap='bone_r')
                for label in ["u", "shortcut", "novel"]:
                    ax3.contour(xxx, yyy, zones[label], levels=0, linewidths=2, colors=colours[label])
                plt.colorbar(pp)
                ax3.axis('off')

                likelihood_true = getattr(session_true, task_label).likelihoods[:, swr_idx]
                means_true = [np.nanmean(np.nansum(likelihood_true[:, zones[zone_label]], axis=1))
                              for zone_label in zone_labels]

                ax4 = plt.subplot(gs1[1:2, 1])
                ax4.bar(np.arange(len(zone_labels)),
                        means_true,
                        color=[colours[zone_label] for zone_label in zone_labels], edgecolor='k')
                ax4.set_xticks(np.arange(len(zone_labels)))
                ax4.set_xticklabels([], rotation=90)
                ax4.set_ylim([0, 1.])
                ax4.set_title("True proportion", fontsize=14)

                likelihood_shuffled = getattr(session_shuffled, task_label).likelihoods[:, swr_idx]

                means_shuffled = [np.nanmean(np.nansum(likelihood_shuffled[:, zones[zone_label]], axis=1))
                                  for zone_label in zone_labels]
                sems_shuffled = [scipy.stats.sem(np.nansum(likelihood_shuffled[:, zones[zone_label]], axis=1))
                                 for zone_label in zone_labels]

                ax5 = plt.subplot(gs1[2:, 1], sharey=ax4)
                ax5.bar(np.arange(len(zone_labels)),
                        means_shuffled,
                        yerr=sems_shuffled,
                        color=[colours[zone_label] for zone_label in zone_labels], edgecolor='k')
                ax5.set_xticks(np.arange(len(zone_labels)))
                ax5.set_xticklabels(zone_labels, rotation=90)
                ax5.set_ylim([0, 1.])
                ax5.set_title("Shuffled proportion", fontsize=14)

                plt.tight_layout()

                if filepath is not None:
                    filename = info.session_id + "_" + task_label + "_summary-swr" + str(swr_idx) + ".png"
                    plt.savefig(os.path.join(filepath, filename))
                    plt.close()
                else:
                    plt.show()


def plot_session(sessions, title, task_labels, zone_labels, colours, filepath=None):

    fig = plt.figure(figsize=(12, 6))
    gs1 = gridspec.GridSpec(1, 4)
    gs1.update(wspace=0.3, hspace=0.)

    for i, zone_label in enumerate(zone_labels):
        sums = {task_label: [] for task_label in task_labels}
        n_swrs = {task_label: 0 for task_label in task_labels}
        for session in sessions:
            for task_label in task_labels:
                zone_sums = getattr(session, task_label).sums(zone_label)
                if zone_sums.size == 1:
                    sums[task_label].extend([np.nan])
                else:
                    sums[task_label].extend(zone_sums)
                    n_swrs[task_label] += getattr(session, task_label).swrs.n_epochs

        for task_label in task_labels:
            sums[task_label] = np.hstack(sums[task_label])

        means = [np.nanmean(sums[task_label])
                 if n_swrs[task_label] != 0 else 0.0
                 for task_label in task_labels]

        sems = [np.nanmean(scipy.stats.sem(sums[task_label], nan_policy="omit"))
                if n_swrs[task_label] != 0 else 0.0
                for task_label in task_labels]

        ax = plt.subplot(gs1[i])
        ax.bar(np.arange(sessions[0].n_tasktimes()),
               means, yerr=sems, color=colours[zone_label])

        ax.set_ylim([0, 1.])

        ax.set_xticks(np.arange(sessions[0].n_tasktimes()))
        ax.set_xticklabels(task_labels, rotation=90)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        if i > 0:
            ax.set_yticklabels([])

        if i == 0:
            ax.set_ylabel("Proportion")

        if zone_label == "other":
            for n_tasktimes, task_label in enumerate(task_labels):
                ax.text(n_tasktimes, 0.01, str(n_swrs[task_label]), ha="center", fontsize=14)

    plt.text(1., 1., "n sessions: "+ str(len(sessions)), horizontalalignment='left',
             verticalalignment='top', fontsize=14)

    fig.suptitle(title, fontsize=16)

    legend_elements = [Patch(facecolor=colours[zone_label], edgecolor='k', label=zone_label)
                       for zone_label in zone_labels]

    plt.legend(handles=legend_elements, bbox_to_anchor=(1., 0.95))

    gs1.tight_layout(fig)

    if filepath is not None:
        plt.savefig(filepath)
        plt.close()
    else:
        plt.show()


def plot_counts_merged(counts, title, task_labels, zone_labels, colours, filepath=None):

    fig = plt.figure(figsize=(12, 6))
    gs1 = gridspec.GridSpec(1, 4)
    gs1.update(wspace=0.3, hspace=0.)

    n_swrs = {task_label: 0 for task_label in task_labels}
    for i, zone_label in enumerate(zone_labels):
        for count in counts:
            for task_label in task_labels:
                n_swrs[task_label] += count[task_label][zone_label]

    for i, zone_label in enumerate(zone_labels):
        merged_counts = {task_label: 0 for task_label in task_labels}
        for count in counts:
            for task_label in task_labels:
                merged_counts[task_label] += count[task_label][zone_label]

        means = [merged_counts[task_label]/n_swrs[task_label]
                 if n_swrs[task_label] != 0 else 0.0
                 for task_label in task_labels]

        ax = plt.subplot(gs1[i])
        ax.bar(np.arange(len(task_labels)), means, color=colours[zone_label])

        ax.set_ylim([0, 1.])

        ax.set_xticks(np.arange(len(task_labels)))
        ax.set_xticklabels(task_labels, rotation=90)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        if i > 0:
            ax.set_yticklabels([])

        if i == 0:
            ax.set_ylabel("Proportion")

        if zone_label == "other":
            for n_tasktimes, task_label in enumerate(task_labels):
                ax.text(n_tasktimes, 0.01, str(n_swrs[task_label]), ha="center", fontsize=14)

    plt.text(1., 1., "n sessions: " + str(len(counts)), horizontalalignment='left',
             verticalalignment='top', fontsize=14)

    fig.suptitle(title, fontsize=16)

    legend_elements = [Patch(facecolor=colours[zone_label], edgecolor='k', label=zone_label)
                       for zone_label in zone_labels]

    plt.legend(handles=legend_elements, bbox_to_anchor=(1., 0.95))

    gs1.tight_layout(fig)

    if filepath is not None:
        plt.savefig(filepath)
        plt.close()
    else:
        plt.show()


def plot_counts_averaged(counts, title, task_labels, zone_labels, colours, filepath=None):

    fig = plt.figure(figsize=(12, 6))
    gs1 = gridspec.GridSpec(1, 4)
    gs1.update(wspace=0.3, hspace=0.)

    proportions = {task_label: {zone_label: [] for zone_label in zone_labels} for task_label in task_labels}
    n_total = {task_label: [] for task_label in task_labels}
    n_swrs = {task_label: 0 for task_label in task_labels}
    for count in counts:
        for task_label in task_labels:
            n_total[task_label] = np.nansum([count[task_label][zone_label] for zone_label in zone_labels])
            for zone_label in zone_labels:
                proportions[task_label][zone_label].append(count[task_label][zone_label]/n_total[task_label])
                n_swrs[task_label] += count[task_label][zone_label]

    for i, zone_label in enumerate(zone_labels):
        means = [np.nanmean(proportions[task_label][zone_label]) for task_label in task_labels]
        sems = [scipy.stats.sem(proportions[task_label][zone_label]) for task_label in task_labels]

        ax = plt.subplot(gs1[i])
        ax.bar(np.arange(len(task_labels)), means, yerr=sems, color=colours[zone_label])

        ax.set_ylim([0, 1.])

        ax.set_xticks(np.arange(len(task_labels)))
        ax.set_xticklabels(task_labels, rotation=90)

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        if i > 0:
            ax.set_yticklabels([])

        if i == 0:
            ax.set_ylabel("Proportion")

        if zone_label == "other":
            for n_tasktimes, task_label in enumerate(task_labels):
                ax.text(n_tasktimes, 0.01, str(n_swrs[task_label]), ha="center", fontsize=14)

    plt.text(1., 1., "n sessions: "+ str(len(counts)), horizontalalignment='left',
             verticalalignment='top', fontsize=14)

    fig.suptitle(title, fontsize=16)

    legend_elements = [Patch(facecolor=colours[zone_label], edgecolor='k', label=zone_label)
                       for zone_label in zone_labels]

    plt.legend(handles=legend_elements, bbox_to_anchor=(1., 0.95))

    gs1.tight_layout(fig)

    if filepath is not None:
        plt.savefig(filepath)
        plt.close()
    else:
        plt.show()


def get_decoded_swr_plots(infos, group, z_thresh=2., power_thresh=3., n_shuffles=100, update_cache=False):

    group = group + "_z-" + str(z_thresh) + "-power-" + str(power_thresh)

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
    swr_params["z_thresh"] = z_thresh
    swr_params["power_thresh"] = power_thresh
    swr_params["merge_thresh"] = 0.02
    swr_params["min_length"] = 0.05
    swr_params["swr_thresh"] = (140.0, 250.0)
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
                                           zone_labels,
                                           save_path=true_path)

        true_sessions.append(true_session)

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
                                               zone_labels,
                                               n_shuffles=n_shuffles,
                                               save_path=shuffled_path)

        shuffled_sessions.append(shuffled_session)

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
                        percentile = scipy.stats.percentileofscore(np.sort(shuffled_sums[:, idx]), true_sums[:, idx])
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
                    passthresh_swrs = None

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

        title = group + "merged-posterior-during-SWRs_passthresh" + str(percentile_thresh) + "-counts"
        filepath = os.path.join(output_filepath, title + ".png")
        plot_counts_merged(passthresh_counts, title, task_labels, zone_labels, colours, filepath)

        title = group + "averaged-posterior-during-SWRs_passthresh" + str(percentile_thresh) + "-counts"
        filepath = os.path.join(output_filepath, title + ".png")
        plot_counts_averaged(passthresh_counts, title, task_labels, zone_labels, colours, filepath)


def main():
    from run import (analysis_infos,
                     r063_infos, r066_infos, r067_infos, r068_infos,
                     days1234_infos, days5678_infos,
                     day1_infos, day2_infos, day3_infos, day4_infos, day5_infos, day6_infos, day7_infos, day8_infos)

    # import info.r063d2 as r063d2
    # import info.r068d8 as r068d8
    # infos = [r063d2, r068d8]
    # group = "test"
    # get_decoded_swr_plots(infos, group=group, n_shuffles=2, update_cache=True)

    info_groups = dict()
    # info_groups["All"] = analysis_infos
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

    get_decoded_swr_plots(analysis_infos, group="All", z_thresh=1., power_thresh=2., update_cache=True)

    for infos, group in zip(info_groups.values(), info_groups.keys()):
        get_decoded_swr_plots(infos, group, z_thresh=1., power_thresh=2., update_cache=False)

    for info in analysis_infos:
        get_decoded_swr_plots([info], info.session_id, z_thresh=1., power_thresh=2., update_cache=False)

    for power_thresh in [3, 4, 5]:
        get_decoded_swr_plots(analysis_infos, group="All", power_thresh=power_thresh, update_cache=True)

        for infos, group in zip(info_groups.values(), info_groups.keys()):
            get_decoded_swr_plots(infos, group, power_thresh=power_thresh, update_cache=False)

        for info in analysis_infos:
            get_decoded_swr_plots([info], info.session_id, power_thresh=power_thresh, update_cache=False)


if __name__ == "__main__":
    main()
