import matplotlib.pyplot as plt
import numpy as np
import os
import nept
import seaborn as sns

import scalebar

from loading_data import get_data
from run import spike_sorted_infos
from utils_maze import speed_threshold


thisdir = os.getcwd()
pickle_filepath = os.path.join(thisdir, "cache", "pickled")
output_filepath = os.path.join(thisdir, "plots", "exploring_swrs")


def plot_swrs_stats(data, texts, task_times, title, ylabel, savepath=None):
    fig, ax = plt.subplots()
    ind = np.arange(len(task_times))

    plt.bar(ind, data)

    labels = ["n=%d" % i for i in texts]
    patches = ax.patches
    for patch, text in zip(patches, labels):
        txt_height = patch.get_height() + (patch.get_height() / 50)
        txt_location = patch.get_x() + (patch.get_width() / 2)
        ax.text(txt_location, txt_height, text, ha='center', va='bottom', size=10)

    ax.set_xticks(ind)
    ax.set_xticklabels(task_times, rotation=75, fontsize=14)
    
    plt.ylabel(ylabel)
    plt.title(title)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath + ".png")
        plt.close("all")
    else:
        plt.show()


def plot_swr(swrs, lfp, position, spikes, buffer=0.15, n_plots=1, savepath=None):
    if swrs.n_epochs < n_plots:
        starts = swrs.starts
        stops = swrs.stops
    else:
        starts = swrs.starts[:n_plots]
        stops = swrs.stops[:n_plots]

    for i, (start, stop) in enumerate(zip(starts, stops)):
        start_time = start - buffer
        stop_time = stop + buffer

        rows = len(spikes)
        add_rows = int(rows / 8)

        ms = 800 / rows
        mew = 0.7
        spike_loc = 1

        fig = plt.figure(figsize=(8, 8))
        ax1 = plt.subplot2grid((rows + add_rows, 2), (0, 0), rowspan=rows)

        # Plotting the spike raster
        for idx, neuron_spikes in enumerate(spikes):
            ax1.plot(neuron_spikes.time, np.ones(len(neuron_spikes.time)) + (idx * spike_loc), '|',
                     color='k', ms=ms, mew=mew)

        ax1.set_xticks([])
        ax1.set_xlim([start_time, stop_time])
        ax1.set_ylim([0.5, len(spikes) * spike_loc + 0.5])

        # Plotting the LFP
        ax2 = plt.subplot2grid((rows + add_rows, 2), (rows, 0), rowspan=add_rows, sharex=ax1)

        start_idx = nept.find_nearest_idx(lfp.time, start_time)
        stop_idx = nept.find_nearest_idx(lfp.time, stop_time)
        ax2.plot(lfp.time[start_idx:stop_idx], lfp.data[start_idx:stop_idx], '#3288bd', lw=0.3)

        start_idx = nept.find_nearest_idx(lfp.time, start)
        stop_idx = nept.find_nearest_idx(lfp.time, stop)
        ax2.plot(lfp.time[start_idx:stop_idx], lfp.data[start_idx:stop_idx], 'r', lw=0.4)

        ax2.set_xticks([])
        ax2.set_xlim([start_time, stop_time])
        ax2.set_yticks([])

        scalebar.add_scalebar(ax2, matchy=False, bbox_transform=fig.transFigure,
                              bbox_to_anchor=(0.5, 0.05), units='ms')

        # Plotting the position
        ax3 = plt.subplot2grid((rows + add_rows, 2), (0, 1), rowspan=int(0.5 * rows))
        ax3.plot(position.x, position.y, '.', color="#bdbdbd", ms=2)

        start_idx = nept.find_nearest_idx(position.time, start_time)
        stop_idx = nept.find_nearest_idx(position.time, stop_time)

        cmap = plt.get_cmap('Oranges')
        colours = cmap(np.linspace(0.25, 0.75, stop_idx - start_idx))

        for j, (x, y) in enumerate(zip(position.x[start_idx:stop_idx], position.y[start_idx:stop_idx])):
            ax3.plot(x, y, ".", color=colours[j])

        ax3.set_xlim(np.min(position.x), np.max(position.x))
        ax3.set_ylim(np.min(position.y), np.max(position.y))
        ax3.axis('off')

        # Cleaning up the plot
        sns.despine(bottom=True)
        plt.tight_layout(h_pad=0.003)

        if savepath is not None:
            plt.savefig(savepath + str(i) + ".png", bbox_inches='tight')
            plt.close("all")
        else:
            plt.show()


def plot_spike_counts(swrs, spikes, task_time, savepath=None):
    spike_counts = []

    for i in range(swrs.n_epochs):
        start = swrs.starts[i]
        stop = swrs.stops[i]
        n_spikes_swr = np.sum([len(spiketrain.time_slice(start, stop).time) for spiketrain in spikes])

        len_swr = stop - start

        start_pre = swrs.starts[i] - len_swr
        stop_pre = swrs.starts[i]
        n_spikes_swr_pre = np.sum([len(spiketrain.time_slice(start_pre, stop_pre).time) for spiketrain in spikes])

        start_post = swrs.stops[i]
        stop_post = swrs.stops[i] + len_swr
        n_spikes_swr_post = np.sum([len(spiketrain.time_slice(start_post, stop_post).time) for spiketrain in spikes])

        spike_counts.append([n_spikes_swr_pre, n_spikes_swr, n_spikes_swr_post])

    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('Greys')

    pp = ax.pcolormesh(spike_counts, vmax=100., cmap=cmap)

    ax.set_xticklabels('')
    ax.set_xticks(np.arange(3)+.5)
    ax.set_xticklabels(['pre','SWR','post'])

    title = info.session_id + ' SWR spike count ' + task_time
    plt.title(title)

    fig.colorbar(pp)

    if savepath is not None:
        plt.savefig(savepath)
    else:
        plt.show()


def plot_swr_stats(info, remove_interneurons, resting_only, plot_example_swr_rasters, plot_swr_spike_counts=False):
    print(info.session_id)
    events, position, spikes, lfp, _ = get_data(info)

    if remove_interneurons:
        max_mean_firing = 5
        interneurons = np.zeros(len(spikes), dtype=bool)
        for i, spike in enumerate(spikes):
            if len(spike.time) / info.session_length >= max_mean_firing:
                interneurons[i] = True
        spikes = spikes[~interneurons]

    task_times = ["prerecord", "phase1", "pauseA", "phase2", "pauseB", "phase3", "postrecord"]

    n_swrs = np.zeros(len(task_times))
    phase_duration = np.zeros(len(task_times))

    for i, task_time in enumerate(task_times):
        if remove_interneurons:
            condition = "_no-interneurons"
        else:
            condition = ""

        epochs_of_interest = info.task_times[task_time]

        phase_duration[i] = epochs_of_interest.durations[0] / 60.

        if resting_only:
            sliced_position = position.time_slice(epochs_of_interest.start, epochs_of_interest.stop)
            epochs_of_interest = speed_threshold(sliced_position, speed_limit=4., rest=True)
            condition = condition + "_rest"

        z_thresh = 2.0
        power_thresh = 3.0
        merge_thresh = 0.02
        min_length = 0.05
        swrs = nept.detect_swr_hilbert(lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                       power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

        # Restrict SWRs to those during epochs of interest and with 4 or more participating neurons
        sliced_spikes = [spiketrain.time_slice(epochs_of_interest.starts, epochs_of_interest.stops) for spiketrain in
                         spikes]

        epochs_of_interest = info.task_times[task_time]

        phase_duration[i] = epochs_of_interest.durations[0] / 60.

        if resting_only:
            sliced_position = position.time_slice(epochs_of_interest.start, epochs_of_interest.stop)
            epochs_of_interest = speed_threshold(sliced_position, speed_limit=4., rest=True)
            condition = condition + "_rest"

        swrs = swrs.intersect(epochs_of_interest)

        swrs = nept.find_multi_in_epochs(sliced_spikes, swrs, min_involved=4)

        if plot_swr_spike_counts:
            savepath = os.path.join(output_filepath, "summary", info.session_id + "_" + task_time + "_swr-spike-count")
            plot_spike_counts(swrs, spikes, task_time, savepath=savepath)

        n_swrs[i] = swrs.n_epochs

        if plot_example_swr_rasters:
            savepath = os.path.join(output_filepath, info.session_id + "_" + task_time + "_swr-raster")
            plot_swr(swrs, lfp, position, sliced_spikes, savepath=savepath)

    title = info.session_id + ' SWRs rate ' + condition
    ylabel = "# swr / minute"
    savepath = os.path.join(output_filepath, "summary", title)
    plot_swrs_stats(n_swrs / phase_duration, n_swrs.astype(int), task_times, title, ylabel, savepath=savepath)

    print("n_swrs:", n_swrs)
    print("swr_rate:", n_swrs / phase_duration)


if __name__ == "__main__":
    # infos = spike_sorted_infos

    import info.r068d5 as r068d5
    infos = [r068d5]

    for info in infos:
        plot_swr_stats(info, remove_interneurons=True,
                       resting_only=False,
                       plot_example_swr_rasters=True,
                       plot_swr_spike_counts=True)

        # plot_swr_stats(info, remove_interneurons=True,
        #                resting_only=True,
        #                plot_example_swr_rasters=True,
        #                plot_swr_spike_counts=True)

        # plot_swr_stats(info, remove_interneurons=False, resting_only=False, plot_example_swr_rasters=False)
        # plot_swr_stats(info, remove_interneurons=True, resting_only=False, plot_example_swr_rasters=False)
        # plot_swr_stats(info, remove_interneurons=False, resting_only=True, plot_example_swr_rasters=False)

        # plot_swr_stats(info, remove_interneurons=False, resting_only=True, plot_example_swr_rasters=False)
        # plot_swr_stats(info, remove_interneurons=True, resting_only=True, plot_example_swr_rasters=False)
        # plot_swr_stats(info, remove_interneurons=True, resting_only=True, plot_example_swr_rasters=True)
