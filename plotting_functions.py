import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import scipy.stats as stats
import seaborn as sns
import pandas as pd

import vdmlab as vdm

from behavior_functions import bytrial_counts, summary_bytrial

sns.set_style('white')
sns.set_style('ticks')
sns.set_context('poster')


def raster_plot(spikes, savepath, savefig=False):
    """Plots raster plot of spikes from multiple neurons.

    Parameters
    ----------
    spikes : list of np.arrays
        Where each inner array contains the spike times (floats) for an individual
        neuron.
    savepath : str
        Location and filename for the saved plot.
    savefig : boolean
        Default is False show the plot without saving it. True and will save the
        plot to the specified location.

    """
    location = 1
    for neuron in spikes:
        if len(neuron) > 0:
            plt.plot(neuron, np.ones(len(neuron))+location, '|', color='k', ms=4, mew=1)
            location += 1
    plt.xlabel('Time (ms)')
    plt.ylabel('Neuron number')
    sns.despine()
    plt.ylim(0, location+1)

    if savefig:
        plt.savefig(savepath, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_sorted_tc(sorted_tc, savepath, savefig=True):
    """Plots sorted tuning curves from a single trajectory for a session.

    Parameters
    ----------
    sorted_tc : list of lists
        Where each inner list contains the tuning curve (floats) for an individual
        neuron.
    savepath : str
        Location and filename for the saved plot.
    savefig : boolean
        Default is True and will save the plot to the specified location.
        False shows with plot without saving it.

    """
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(sorted_tc, cmap='YlGn')
    plt.ylim(0, len(sorted_tc))
    plt.xlim(0, len(sorted_tc[0]))
    plt.ylabel('Neuron number')
    plt.xlabel('Location (cm)')
    plt.colorbar(heatmap)
    ax.tick_params(labelsize='small')
    sns.despine()
    plt.tight_layout()

    if savefig:
        plt.savefig(savepath, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# Behavior
def plot_intersects(zone):
    """Plots intersections of zones of ideal trajectory

    Parameters
    ----------
    zone : Shapely's Polygon object

    """
    for intersect in zone:
        plt.plot(intersect.exterior.xy[0], intersect.exterior.xy[1], 'b', lw=1)


def plot_zone(zone):
    """Plots zone of ideal trajectory

        Parameters
        ----------
        zone : Shapely's Polygon object

        """
    plt.plot(zone.exterior.xy[0], zone.exterior.xy[1], 'b', lw=1)


def plot_bydurations(durations, savepath, savefig=True):
    """Plots duration for each trial separated by trajectories. Behavior only.

        Parameters
        ----------
        durations : dict
            With u, shortcut, novel, num_sessions as keys.
            Each value is a list of durations (float) for a each session.
        savepath : str
            Location and filename for the saved plot.
        savefig : boolean
            Default is True and will save the plot to the specified location. False
            shows with plot without saving it.

        """
    ax = sns.boxplot(data=[durations['u'], durations['shortcut'], durations['novel']])
    sns.color_palette("hls", 18)
    ax.set(xticklabels=['U', 'Shortcut', 'Novel'])
    plt.ylabel('Duration of trial (s)')
    plt.xlabel('sessions=' + str(durations['num_sessions']))
    plt.ylim(0, 140)
    sns.despine()

    if savefig:
        plt.savefig(savepath, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_proportions(us, shortcuts, novels, savepath, savefig=True):
    """Plots proportion of each trajectory taken. Behavior only.

        Parameters
        ----------
        us : list of floats
            Proportion along the u trajectory for each session.
            len(us) == num_sessions evaluated
        shortcuts : list of floats
            Proportion along the shortcut trajectory for each session.
            len(shortcut) == num_sessions evaluated
        novels : list of floats
            Proportion along the novel trajectory for each session.
            len(novel) == num_sessions evaluated
        savepath : str
            Location and filename for the saved plot.
        savefig : boolean
            Default is True and will save the plot to the specified location. False
            shows with plot without saving it.

        """
    all_us = np.mean(us)
    us_sem = stats.sem(us)
    all_shortcuts = np.mean(shortcuts)
    shortcuts_sem = stats.sem(shortcuts)
    all_novels = np.mean(novels)
    novels_sem = stats.sem(novels)

    n_groups = list(range(3))

    colour = ['#5975a4', '#5f9e6e', '#b55d5f']

    data = [all_us, all_shortcuts, all_novels]
    sems = [us_sem, shortcuts_sem, novels_sem]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i in list(range(len(data))):
        ax.bar(n_groups[i], data[i], align='center',
               yerr=sems[i], color=colour[i], ecolor='#525252')

    plt.xlabel('(sessions=' + str(len(us)) + ')')
    plt.ylabel('Proportion of trials')
    sns.despine()
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.xticks(n_groups, ['U', 'Shortcut', 'Novel'])

    # plt.tight_layout()
    if savefig:
        plt.savefig(savepath, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_bytrial(togethers, savepath, min_length=30, savefig=True):
    """Plots choice of trajectory by trial. Behavior only.

        Parameters
        ----------
        togethers : list
        savepath : str
            Location and filename for the saved plot.
        min_length = int
            This is the number of trials to be considered.
            The default is set to 30 (Eg. trials 1-30 are considered).
        savefig : boolean
            Default is True and will save the plot to the specified location.
            False shows with plot without saving it.

        """
    bytrial = bytrial_counts(togethers, min_length)

    means, sems = summary_bytrial(bytrial, min_length)

    trials = list(range(min_length))

    colours = dict(u='#5975a4', shortcut='#5f9e6e', novel='#b55d5f')
    labels = dict(u='Full U', shortcut='Shortcut', novel='Novel')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for path in means:
        ax.plot(trials, means[path], color=colours[path], label=labels[path], marker='o', lw=2)
        ax.fill_between(trials, np.array(means[path]) - np.array(sems[path]),
                        np.array(means[path]) + np.array(sems[path]),
                        color=colours[path], interpolate=True, alpha=0.3)
    plt.ylabel('Proportion of trials')
    plt.xlabel('Trial number (sessions=' + str(len(togethers)) + ')')
    sns.despine()
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.legend(loc=1, prop={'size': 10})

    if savefig:
        plt.savefig(savepath, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# Place fields
def plot_fields(heatmaps, position, num_neurons, savepath=None, savefig=True, plot_log=True, num_bins=100, vmax=None):
    """Plots spiking in 2D position space.

        Parameters
        ----------
        heatmaps : dict of lists
            Where the key is the neuron number and the value is the heatmap for
            that individual neuron.
        position : vdmlab.Position
        savepath : str
            Location and filename for the saved plot.
        num_neurons = int
            Number of neurons used for this plot.
        savefig : boolean
            Default is True and will save the plot to the specified location.
            False shows with plot without saving it.
        plot_log : boolean
            Range for plot in log scale. Allows for better visualization of
            areas with large amount of spikes. Default is set to True.
        num_bins : int
            Number of bins the 2D space is divided into.
            Default is set to 100.
        vmax : float, optional
            Default is set to None. Used to scale the heatmaps for different
            neurons or sessions to better directly compare.

        """
    plt.figure()
    plt.plot(position.x, position.y, 'k.', ms=0.2)
    xedges = np.linspace(np.min(position.x)-2, np.max(position.x)+2, num_bins+1)
    yedges = np.linspace(np.min(position.y)-2, np.max(position.y)+2, num_bins+1)
    xx, yy = np.meshgrid(xedges, yedges)

    if plot_log:
        pp = plt.pcolormesh(xx, yy, heatmaps, norm=SymLogNorm(linthresh=1.0, vmax=vmax), cmap='YlGn')
    else:
        pp = plt.pcolormesh(xx, yy, heatmaps, vmax=vmax, cmap='YlGn')
    print(np.max(heatmaps))
    plt.colorbar(pp)
    plt.axis('off')
    plt.text(2, 6, r'n=' + str(num_neurons), fontsize=15)

    if savefig:
        plt.savefig(savepath, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# Co-occurrence
def plot_cooccur(probs, savepath=None):
    """Plots co-occurrence probabilities from p0, p2, p3, p4.

        Parameters
        ----------
        probs : dict
            Where the keys are active (dict), expected (dict), observed (dict), zscore (dict).
            Each dictionary contains trajectories (u, shortcut, novel).
        savepath : str or None
            Location and filename for the saved plot.

        """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ind = np.arange(3)
    width = 0.8
    colours = ['#5975a4', '#5f9e6e', '#b55d5f']

    active_means = [np.nanmean(probs['u']['active']),
                    np.nanmean(probs['shortcut']['active']),
                    np.nanmean(probs['novel']['active'])]
    active_sems = [stats.sem(probs['u']['active'], nan_policy='omit'),
                   stats.sem(probs['shortcut']['active'], nan_policy='omit'),
                   stats.sem(probs['novel']['active'], nan_policy='omit')]
    ax1.bar(ind, active_means, width, color=colours, yerr=active_sems, ecolor='k')
    ax1.set_ylabel('Proportion of SWRs active')
    ax1.set_title('Probability that a given neuron is active')
    ax1.set_xticks(ind + width*0.5)
    ax1.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.get_xaxis().tick_bottom()
    ax1.get_yaxis().tick_left()

    expected_means = [np.nanmean(probs['u']['expected']),
                      np.nanmean(probs['shortcut']['expected']),
                      np.nanmean(probs['novel']['expected'])]
    expected_sems = [stats.sem(probs['u']['expected'], nan_policy='omit'),
                     stats.sem(probs['shortcut']['expected'], nan_policy='omit'),
                     stats.sem(probs['novel']['expected'], nan_policy='omit')]
    ax2.bar(ind, expected_means, width, color=colours, yerr=expected_sems, ecolor='k')
    ax2.set_ylabel('Expected conditional probability')
    ax2.set_title('Observed conditional probabilities, given independence')
    ax2.set_xticks(ind + width*0.5)
    ax2.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.get_xaxis().tick_bottom()
    ax2.get_yaxis().tick_left()

    observed_means = [np.nanmean(probs['u']['observed']),
                      np.nanmean(probs['shortcut']['observed']),
                      np.nanmean(probs['novel']['observed'])]
    observed_sems = [stats.sem(probs['u']['observed'], nan_policy='omit'),
                     stats.sem(probs['shortcut']['observed'], nan_policy='omit'),
                     stats.sem(probs['novel']['observed'], nan_policy='omit')]
    ax3.bar(ind, observed_means, width, color=colours, yerr=observed_sems, ecolor='k')
    ax3.set_ylabel('Cell pair joint probability')
    ax3.set_title('Observed co-activity')
    ax3.set_xticks(ind + width*0.5)
    ax3.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.get_xaxis().tick_bottom()
    ax3.get_yaxis().tick_left()

    zscore_means = [np.nanmean(probs['u']['zscore']),
                      np.nanmean(probs['shortcut']['zscore']),
                      np.nanmean(probs['novel']['zscore'])]
    zscore_sems = [stats.sem(probs['u']['zscore'], nan_policy='omit'),
                     stats.sem(probs['shortcut']['zscore'], nan_policy='omit'),
                     stats.sem(probs['novel']['zscore'], nan_policy='omit')]
    ax4.bar(ind, zscore_means, width, color=colours, yerr=zscore_sems, ecolor='k')
    ax4.set_ylabel('SWR co-activation z-scored')
    ax4.set_title('Co-activation above chance levels')
    ax4.set_xticks(ind + width*0.5)
    ax4.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.get_xaxis().tick_bottom()
    ax4.get_yaxis().tick_left()

    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()


def plot_cooccur_combined(combined, total_epochs, savepath=None):
    """Plots co-occurrence probabilities from p0, p2, p3, p4.

        Parameters
        ----------
        combined : dict
            Where the keys are active (dict), expected (dict), observed (dict), zscore (dict).
            Each dictionary contains trajectories (u, shortcut, novel).
        total_epochs: int
        savepath : str or None
            Location and filename for the saved plot.

        """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ind = np.arange(3)
    width = 0.8
    colours = ['#5975a4', '#5f9e6e', '#b55d5f']

    active_means = [np.sum(combined['u']['active'])/total_epochs,
                    np.sum(combined['shortcut']['active'])/total_epochs,
                    np.sum(combined['novel']['active'])/total_epochs]
    ax1.bar(ind, active_means, width, color=colours)
    ax1.set_ylabel('Proportion of SWRs active')
    ax1.set_title('Probability that a given neuron is active')
    ax1.set_xticks(ind + width*0.5)
    ax1.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.get_xaxis().tick_bottom()
    ax1.get_yaxis().tick_left()

    expected_means = [np.sum(combined['u']['expected'])/total_epochs,
                      np.sum(combined['shortcut']['expected'])/total_epochs,
                      np.sum(combined['novel']['expected'])/total_epochs]
    ax2.bar(ind, expected_means, width, color=colours)
    ax2.set_ylabel('Expected conditional probability')
    ax2.set_title('Observed conditional probabilities, given independence')
    ax2.set_xticks(ind + width*0.5)
    ax2.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.get_xaxis().tick_bottom()
    ax2.get_yaxis().tick_left()

    observed_means = [np.sum(combined['u']['observed'])/total_epochs,
                      np.sum(combined['shortcut']['observed'])/total_epochs,
                      np.sum(combined['novel']['observed'])/total_epochs]
    ax3.bar(ind, observed_means, width, color=colours)
    ax3.set_ylabel('Cell pair joint probability')
    ax3.set_title('Observed co-activity')
    ax3.set_xticks(ind + width*0.5)
    ax3.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.get_xaxis().tick_bottom()
    ax3.get_yaxis().tick_left()

    zscore_means = [np.sum(combined['u']['zscore'])/total_epochs,
                      np.sum(combined['shortcut']['zscore'])/total_epochs,
                      np.sum(combined['novel']['zscore'])/total_epochs]
    ax4.bar(ind, zscore_means, width, color=colours)
    ax4.set_ylabel('SWR co-activation z-scored')
    ax4.set_title('Co-activation above chance levels')
    ax4.set_xticks(ind + width*0.5)
    ax4.set_xticklabels(('U', 'Shortcut', 'Novel'))
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.get_xaxis().tick_bottom()
    ax4.get_yaxis().tick_left()

    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()


def plot_swrs(lfp, swrs, saveloc=None, row=10, col=8, buffer=20, savefig=True):
    """Plots all local field potentials (LFP) around sharp-wave ripple (SWR) times
        for each given SWR.

        Parameters
        ----------
        lfp : vdmlab.LFP
        swrs : list
            Contains vdmlab.LFP objects
        saveloc : str or None
            Location and filename for the saved plot. Do not add '.png', it is
            added here to include the multiple figures into the filename.
        row = int
            Number of rows in each figure.
        col : int
            Number of columns in each figure.
        buffer : int
            Amount of LFP shown on either side of SWR.
        savefig : boolean
            Default is True and will save the plot to the specified location.
            False shows with plot without saving it.

    """
    plots_per_fig = row * col
    num_figures = range(int(np.ceil(len(swrs) / plots_per_fig)))

    for fig in num_figures:
        print('figure', fig, 'of', np.max(list(num_figures)))
        plt.figure(fig)

        stop_idx = plots_per_fig * (fig + 1)
        start_idx = stop_idx - plots_per_fig
        if stop_idx > len(swrs):
            stop_idx = len(swrs) + 1

        for i, swr in enumerate(swrs[start_idx:stop_idx]):
            start = vdm.find_nearest_idx(lfp.time, swr.time[0])
            stop = vdm.find_nearest_idx(lfp.time, swr.time[-1])
            plt.subplot(row, col, i + 1)

            plt.plot(lfp.time[start-buffer:stop+buffer], lfp.data[start-buffer:stop+buffer], 'k')
            plt.plot(swr.time, swr.data, 'r')

            plt.axis('off')

        if savefig:
            plt.savefig(saveloc + str(fig + 1) + '.png', dpi=300)
            plt.close()
        else:
            plt.show()


def plot_decoded(decoded, y_label, savepath=None):
    """Plots barplot.

    Parameters
    ----------
    decoded: dict
        With u, shortcut, novel as keys, each a vdmlab.Position object.
    y_label: str
    savepath : str or None
        Location and filename for the saved plot.

    """
    u_dict = dict(total=decoded['u'], trajectory='U')
    shortcut_dict = dict(total=decoded['shortcut'], trajectory='Shortcut')
    novel_dict = dict(total=decoded['novel'], trajectory='Novel')

    u = pd.DataFrame(u_dict)
    shortcut = pd.DataFrame(shortcut_dict)
    novel = pd.DataFrame(novel_dict)
    data = pd.concat([u, shortcut, novel])

    plt.figure()
    ax = sns.barplot(x='trajectory', y='total', data=data, palette='colorblind')
    sns.axlabel(xlabel=' ', ylabel=y_label, fontsize=16)

    sns.despine()
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()


def plot_decoded_pause(decode, total_times, savepath=None):
    """Plots barplot of time decoded in each trajectory by total time.

    Parameters
    ----------
    decode: dict
        With u, shortcut, novel as keys.
    total_times: list
        Number of total time bins for each session.
    savepath : str or None
        Location and filename for the saved plot.

    """
    normalized = dict(u=[], shortcut=[], novel=[])
    for key in normalized:
        for session in range(len(total_times)):
            normalized[key].append(len(decode[key][session].time)/total_times[session])

    u_dict = dict(total=normalized['u'], trajectory='U')
    shortcut_dict = dict(total=normalized['shortcut'], trajectory='Shortcut')
    novel_dict = dict(total=normalized['novel'], trajectory='Novel')

    u = pd.DataFrame(u_dict)
    shortcut = pd.DataFrame(shortcut_dict)
    novel = pd.DataFrame(novel_dict)
    data = pd.concat([u, shortcut, novel])

    plt.figure()
    ax = sns.barplot(x='trajectory', y='total', data=data, palette='colorblind')
    sns.axlabel(xlabel=' ', ylabel="Proportion of time", fontsize=16)

    sns.despine()
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()


def plot_decoded_errors(decode_errors, shuffled_errors, savepath=None):
    """Plots boxplot distance between decoded and actual position for decoded and shuffled_id.

    Parameters
    ----------
    decode_errors: list of np.arrays
    shuffled_errors: list of np.arrays
    savepath : str or None
        Location and filename for the saved plot.

    """
    decoded_dict = dict(error=decode_errors, shuffled='Decoded')
    shuffled_dict = dict(error=shuffled_errors, shuffled='ID-shuffle decoded')
    decoded = pd.DataFrame(decoded_dict)
    shuffled = pd.DataFrame(shuffled_dict)
    data = pd.concat([shuffled, decoded])

    plt.figure()
    flierprops = dict(marker='o', markersize=2, linestyle='none')
    ax = sns.boxplot(x='shuffled', y='error', data=data, palette="Set2", flierprops=flierprops)

    sns.axlabel(xlabel=' ', ylabel="Error (cm)", fontsize=16)

    plt.tight_layout()
    sns.despine()

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()


def plot_compare_decoded_pauses(decoded_1, times_1, decoded_2, times_2, labels, savepath=None):
    """Plots barplot comparing decoded during two phases

    Parameters
    ----------
    decoded_1: dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object.
    times_1: list of floats
    decoded_2: dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object.
    times_2: list of floats
    labels: list of str
    savepath : str or None
        Location and filename for the saved plot.

    """
    decode_1 = dict(u=[], shortcut=[], novel=[])
    for key in decode_1:
        for session in range(len(times_1)):
            decode_1[key].append(len(decoded_1[key][session].time)/times_1[session])

    u_dict1 = dict(total=decode_1['u'], trajectory='U', exp_time=labels[0])
    shortcut_dict1 = dict(total=decode_1['shortcut'], trajectory='Shortcut', exp_time=labels[0])
    novel_dict1 = dict(total=decode_1['novel'], trajectory='Novel', exp_time=labels[0])

    u1 = pd.DataFrame(u_dict1)
    shortcut1 = pd.DataFrame(shortcut_dict1)
    novel1 = pd.DataFrame(novel_dict1)

    decode_2 = dict(u=[], shortcut=[], novel=[])
    for key in decode_2:
        for session in range(len(times_2)):
            decode_2[key].append(len(decoded_2[key][session].time)/times_2[session])

    u_dict2 = dict(total=decode_2['u'], trajectory='U', exp_time=labels[1])
    shortcut_dict2 = dict(total=decode_2['shortcut'], trajectory='Shortcut', exp_time=labels[1])
    novel_dict2 = dict(total=decode_2['novel'], trajectory='Novel', exp_time=labels[1])

    u2 = pd.DataFrame(u_dict2)
    shortcut2 = pd.DataFrame(shortcut_dict2)
    novel2 = pd.DataFrame(novel_dict2)
    data = pd.concat([u1, shortcut1, novel1, u2, shortcut2, novel2])

    def plot_v3(data, exp_labels):
        fig = sns.FacetGrid(data, col='trajectory', col_order=['U', 'Shortcut', 'Novel'], sharex=False)

        fig.map(sns.barplot, 'trajectory', 'total', 'exp_time',  hue_order=[exp_labels[0], exp_labels[1]])
        axes = np.array(fig.axes.flat)

        return plt.gcf(), axes

    def set_labels(fig, axes, exp_labels):
        labels = ['U', 'Shortcut', 'Novel']

        for i, ax in enumerate(axes):
            ax.set_xticks([-.2, .2])
            ax.set_xticklabels([exp_labels[0], exp_labels[1]])
            ax.set_xlabel(labels[i])
            ax.set_ylabel('')
            ax.set_title('')

        axes.flat[0].set_ylabel('Proportion of time')

        sns.despine(ax=axes[1], left=True)
        sns.despine(ax=axes[2], left=True)

    def set_style():
        plt.style.use(['seaborn-white', 'seaborn-paper'])

    def color_bars(axes):
        colors = sns.color_palette('Set2')
        for i in range(3):
            p1, p2 = axes[i].patches

            p1.set_color(colors[i])
            p1.set_edgecolor('k')

            p2.set_color(colors[i])
            p2.set_edgecolor('k')
            p2.set_hatch('//')

    def set_size(fig):
        fig.set_size_inches(6, 4)
        plt.tight_layout()

    set_style()
    fig, axes = plot_v3(data, labels)
    set_labels(fig, axes, labels)
    color_bars(axes)
    set_size(fig)

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()



def plot_weighted_cooccur_pauses(cooccur_1, epochs_1, cooccur_2, epochs_2, labels, savepath=None):
    """Plots barplot comparing cooccur z-score during two phases

    Parameters
    ----------
    cooccur_1: dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object.
    epochs_1: list of ints
    cooccur_2: dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object.
    epochs_2: list of ints
    labels: list of str
    savepath : str or None
        Location and filename for the saved plot.

    """
    cooccurs_1 = dict(u=[], shortcut=[], novel=[])
    for key in cooccurs_1:
        for session in range(len(epochs_1)):
            cooccurs_1[key].append(np.sum(cooccur_1[key]['zscore'][session])/epochs_1[session])

    u_dict1 = dict(total=cooccurs_1['u'], trajectory='U', exp_time=labels[0])
    shortcut_dict1 = dict(total=cooccurs_1['shortcut'], trajectory='Shortcut', exp_time=labels[0])
    novel_dict1 = dict(total=cooccurs_1['novel'], trajectory='Novel', exp_time=labels[0])

    u1 = pd.DataFrame(u_dict1)
    shortcut1 = pd.DataFrame(shortcut_dict1)
    novel1 = pd.DataFrame(novel_dict1)

    cooccurs_2 = dict(u=[], shortcut=[], novel=[])
    for key in cooccurs_2:
        for session in range(len(epochs_2)):
            cooccurs_2[key].append(np.sum(cooccur_2[key]['zscore'][session])/epochs_2[session])

    u_dict2 = dict(total=cooccurs_2['u'], trajectory='U', exp_time=labels[1])
    shortcut_dict2 = dict(total=cooccurs_2['shortcut'], trajectory='Shortcut', exp_time=labels[1])
    novel_dict2 = dict(total=cooccurs_2['novel'], trajectory='Novel', exp_time=labels[1])

    u2 = pd.DataFrame(u_dict2)
    shortcut2 = pd.DataFrame(shortcut_dict2)
    novel2 = pd.DataFrame(novel_dict2)
    data = pd.concat([u1, shortcut1, novel1, u2, shortcut2, novel2])

    def plot_v3(data, exp_labels):
        fig = sns.FacetGrid(data, col='trajectory', col_order=['U', 'Shortcut', 'Novel'], sharex=False)

        fig.map(sns.barplot, 'trajectory', 'total', 'exp_time',  hue_order=[exp_labels[0], exp_labels[1]])
        axes = np.array(fig.axes.flat)

        return plt.gcf(), axes

    def set_labels(fig, axes, exp_labels):
        labels = ['U', 'Shortcut', 'Novel']

        for i, ax in enumerate(axes):
            ax.set_xticks([-.2, .2])
            ax.set_xticklabels([exp_labels[0], exp_labels[1]])
            ax.set_xlabel(labels[i])
            ax.set_ylabel('')
            ax.set_title('')

        axes.flat[0].set_ylabel('Proportion of time')

        sns.despine(ax=axes[1], left=True)
        sns.despine(ax=axes[2], left=True)

    def set_style():
        plt.style.use(['seaborn-white', 'seaborn-paper'])

    def color_bars(axes):
        colors = sns.color_palette('Set2')
        for i in range(3):
            p1, p2 = axes[i].patches

            p1.set_color(colors[i])
            p1.set_edgecolor('k')

            p2.set_color(colors[i])
            p2.set_edgecolor('k')
            p2.set_hatch('//')

    def set_size(fig):
        fig.set_size_inches(6, 4)
        plt.tight_layout()

    set_style()
    fig, axes = plot_v3(data, labels)
    set_labels(fig, axes, labels)
    color_bars(axes)
    set_size(fig)

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()


def plot_cooccur_pauses(cooccur_1, cooccur_2, labels, savepath=None):
    """Plots barplot comparing cooccur z-score during two phases

    Parameters
    ----------
    cooccur_1: dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object.
    cooccur_2: dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object.
    labels: list of str
    savepath : str or None
        Location and filename for the saved plot.

    """

    cooccurs_1 = dict(u=[], shortcut=[], novel=[])
    for key in cooccurs_1:
        for session in range(len(cooccur_1)):
            cooccurs_1[key].append(cooccur_1[key]['zscore'][session])

    u_dict1 = dict(total=cooccurs_1['u'], trajectory='U', exp_time=labels[0])
    shortcut_dict1 = dict(total=cooccurs_1['shortcut'], trajectory='Shortcut', exp_time=labels[0])
    novel_dict1 = dict(total=cooccurs_1['novel'], trajectory='Novel', exp_time=labels[0])

    u1 = pd.DataFrame(u_dict1)
    shortcut1 = pd.DataFrame(shortcut_dict1)
    novel1 = pd.DataFrame(novel_dict1)

    cooccurs_2 = dict(u=[], shortcut=[], novel=[])
    for key in cooccurs_2:
        for session in range(len(cooccur_2)):
            cooccurs_2[key].append(cooccur_2[key]['zscore'][session])

    u_dict2 = dict(total=cooccurs_2['u'], trajectory='U', exp_time=labels[1])
    shortcut_dict2 = dict(total=cooccurs_2['shortcut'], trajectory='Shortcut', exp_time=labels[1])
    novel_dict2 = dict(total=cooccurs_2['novel'], trajectory='Novel', exp_time=labels[1])

    u2 = pd.DataFrame(u_dict2)
    shortcut2 = pd.DataFrame(shortcut_dict2)
    novel2 = pd.DataFrame(novel_dict2)
    data = pd.concat([u1, shortcut1, novel1, u2, shortcut2, novel2])

    def plot_v3(data, exp_labels):
        fig = sns.FacetGrid(data, col='trajectory', col_order=['U', 'Shortcut', 'Novel'], sharex=False)

        fig.map(sns.barplot, 'trajectory', 'total', 'exp_time',  hue_order=[exp_labels[0], exp_labels[1]])
        axes = np.array(fig.axes.flat)

        return plt.gcf(), axes

    def set_labels(fig, axes, exp_labels):
        labels = ['U', 'Shortcut', 'Novel']

        for i, ax in enumerate(axes):
            ax.set_xticks([-.2, .2])
            ax.set_xticklabels([exp_labels[0], exp_labels[1]])
            ax.set_xlabel(labels[i])
            ax.set_ylabel('')
            ax.set_title('')

        axes.flat[0].set_ylabel('Proportion of time')

        sns.despine(ax=axes[1], left=True)
        sns.despine(ax=axes[2], left=True)

    def set_style():
        plt.style.use(['seaborn-white', 'seaborn-paper'])

    def color_bars(axes):
        colors = sns.color_palette('Set2')
        for i in range(3):
            p1, p2 = axes[i].patches

            p1.set_color(colors[i])
            p1.set_edgecolor('k')

            p2.set_color(colors[i])
            p2.set_edgecolor('k')
            p2.set_hatch('//')

    def set_size(fig):
        fig.set_size_inches(6, 4)
        plt.tight_layout()

    set_style()
    fig, axes = plot_v3(data, labels)
    set_labels(fig, axes, labels)
    color_bars(axes)
    set_size(fig)

    if savepath is not None:
        plt.savefig(savepath, dpi=300)
        plt.close()
    else:
        plt.show()
