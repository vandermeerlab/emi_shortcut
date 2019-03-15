import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import numpy as np
import scipy
import scalebar
import os
import nept

from loading_data import get_data
from utils_maze import get_bin_centers


def plot_session(sessions, title, task_labels, zone_labels, colours, filepath=None):

    fig = plt.figure(figsize=(12, 6))
    gs1 = gridspec.GridSpec(1, 4)
    gs1.update(wspace=0.3, hspace=0.)

    n_session_above_thresh = {task_label: 0 for task_label in task_labels}
    for session in sessions:
        for task_label in task_labels:
            likelihoods = getattr(session, task_label).likelihoods
            if likelihoods.shape[1] > 1:
                n_session_above_thresh[task_label] += 1

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
                ax.text(n_tasktimes, 0.01, str(n_swrs[task_label]), ha="center", fontsize=10)

    plt.text(1., 1., "n sessions: " + str(len(sessions)), horizontalalignment='left',
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
        means = [np.nanmean(proportions[task_label][zone_label])
                 if n_swrs[task_label] != 0 else 0
                 for task_label in task_labels]

        sems = [scipy.stats.sem(proportions[task_label][zone_label], nan_policy="omit")
                if n_swrs[task_label] != 0 else 0
                for task_label in task_labels]

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
