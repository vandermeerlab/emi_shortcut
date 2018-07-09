import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import scipy.stats as stats
from collections import OrderedDict
import seaborn as sns
import pandas as pd

import nept

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
        plt.savefig(savepath, bbox_inches='tight', transparent=True)
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
        plt.savefig(savepath, bbox_inches='tight', transparent=True)
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


def plot_durations(durations, savepath, n_sessions, early_late=False, figsize=(8, 5), fliersize=3, savefig=True):
    """ Plots duration of each trajectory taken. Behavior only.

    Parameters
    ----------
    durations : pd.DataFrame
        With trajectory and value columns.
        For comparison, also a time column.
    savepath : str
        Location and filename for the saved plot.
    n_sessions: int
    early_late: boolean
    figsize : tuple
        Width by height in inches.
    savefig : boolean
        Default is True and will save the plot to the specified location. False
        shows with plot without saving it.

    """
    plt.figure(figsize=(8, 5))

    flierprops = dict(marker='o', markersize=fliersize, linestyle='none')

    if early_late:
        colour = ['#bf812d', '#35978f']
        ax = sns.boxplot(x="trajectory", y="value", hue="time", data=durations, palette=colour,
                         flierprops=flierprops)

    else:
        colour = ['#0072b2', '#009e73', '#d55e00']
        ax = sns.boxplot(x="trajectory", y="value", data=durations, palette=colour,
                         flierprops=flierprops)

    ax.set(xticklabels=['U', 'Shortcut', 'Dead-end'])
    plt.ylabel('Duration of trial (s)')
    plt.xlabel('(sessions=' + str(n_sessions) + ')')
    plt.ylim(0, 120)
    sns.despine(left=False)

    plt.tight_layout()

    if savefig:
        plt.savefig(savepath, transparent=True)
        plt.close()
    else:
        plt.show()


def plot_proportions(proportions, savepath, n_sessions, early_late=False, figsize=(8, 5), savefig=True):
    """ Plots proportion of each trajectory taken. Behavior only.

    Parameters
    ----------
    proportions : pd.DataFrame
        With trajectory and value columns.
        For comparison, also a time column.
    n_sessions: int
    early_late: boolean
    savepath : str
        Location and filename for the saved plot.
    figsize : tuple
        Width by height in inches.
    savefig : boolean
        Default is True and will save the plot to the specified location. False
        shows with plot without saving it.

    """

    plt.figure(figsize=figsize)

    if early_late:
        colour = ['#bf812d', '#35978f']
        ax = sns.barplot(x="trajectory", y="value", hue="time", data=proportions, palette=colour)

    else:
        colour = ['#0072b2', '#009e73', '#d55e00']
        ax = sns.barplot(x="trajectory", y="value", data=proportions, palette=colour)


    ax.set(xticklabels=['U', 'Shortcut', 'Dead-end'])
    plt.ylabel('Proportion of trials')
    plt.xlabel('(sessions=' + str(n_sessions) + ')')
    sns.despine(left=False)

    plt.tight_layout()

    if savefig:
        plt.savefig(savepath, transparent=True)
        plt.close()
    else:
        plt.show()


def plot_bytrial(means, sems, n_sessions, savepath, figsize=(6., 3), savefig=True):
    """Plots choice of trajectory by trial. Behavior only.

    Parameters
    ----------
    togethers : list
    savepath : str
        Location and filename for the saved plot.
    min_length = int
        This is the number of trials to be considered.
        The default is set to 30 (Eg. trials 1-30 are considered).
    figsize : tuple
        Width by height in inches.
    savefig : boolean
        Default is True and will save the plot to the specified location.
        False shows with plot without saving it.

    """
    trials = list(range(1, len(means['u'])+1))

    colours = dict(u='#0072b2', shortcut='#009e73', novel='#d55e00')
    labels = dict(u='U', shortcut='Shortcut', novel='Dead-end')

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    for path in means:
        ax.plot(trials, means[path], color=colours[path], label=labels[path], marker='o', lw=1)
        ax.fill_between(trials, np.array(means[path]) - np.array(sems[path]),
                        np.array(means[path]) + np.array(sems[path]),
                        color=colours[path], interpolate=True, alpha=0.2)
    plt.ylabel('Proportion of trials')
    # plt.title('Early')
    # ax.set(yticklabels=[], yticks=[])
    plt.xlabel('Trial number (sessions=' + str(n_sessions) + ')')
    plt.ylim(0.0, 1.0)
    sns.despine(left=False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.legend(loc=1, bbox_to_anchor=(1.2, 1.1))

    if savefig:
        plt.savefig(savepath, bbox_inches='tight', transparent=True)
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
        position : nept.Position
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
    plt.figure(figsize=(5, 4))
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
        plt.savefig(savepath, bbox_inches='tight', transparent=True)
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
    colours = ['#0072b2', '#009e73',  '#d55e00']

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
        plt.savefig(savepath, transparent=True)
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
    colours = ['#0072b2', '#009e73',  '#d55e00']

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
        plt.savefig(savepath, transparent=True)
        plt.close()
    else:
        plt.show()


def plot_swrs(lfp, swrs, saveloc=None, row=10, col=8, buffer=20, savefig=True):
    """Plots all local field potentials (LFP) around sharp-wave ripple (SWR) times
        for each given SWR.

        Parameters
        ----------
        lfp : nept.LFP
        swrs : list
            Contains nept.LFP objects
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
    n_figures = range(int(np.ceil(swrs.n_epochs / plots_per_fig)))

    for fig in n_figures:
        print('figure', fig, 'of', np.max(list(n_figures)))
        plt.figure(fig)

        stop_idx = plots_per_fig * (fig + 1)
        start_idx = stop_idx - plots_per_fig
        if stop_idx > swrs.n_epochs:
            stop_idx = swrs.n_epochs + 1

        for i, (starts, stops) in enumerate(zip(swrs.starts[start_idx:stop_idx], swrs.stops[start_idx:stop_idx])):
            start = nept.find_nearest_idx(lfp.time, starts)
            stop = nept.find_nearest_idx(lfp.time, stops)
            plt.subplot(row, col, i+1)

            plt.plot(lfp.time[start-buffer:stop+buffer], lfp.data[start-buffer:stop+buffer], 'k')
            plt.plot(lfp.time[start:stop], lfp.data[start:stop], 'r')

            plt.axis('off')

        if savefig:
            plt.savefig(saveloc + str(fig + 1) + '.png', transparent=True)
            plt.close()
        else:
            plt.show()


def plot_decoded_errors(decode_errors, shuffled_errors, experiment_time, fliersize=1, savepath=None, transparent=False):
    """Plots boxplot distance between decoded and actual position for decoded and shuffled_id

    Parameters
    ----------
    decode_errors: dict of lists
        With u, shortcut, novel, other, and together as keys.
    shuffled_errors: dict of lists
        With u, shortcut, novel, other, and together as keys.
    fliersize: int
    savepath : str or None
        Location and filename for the saved plot.

    """
    decoded_dict = dict(error=decode_errors[experiment_time]['together'], shuffled='Decoded')
    shuffled_dict = dict(error=shuffled_errors[experiment_time]['together'], shuffled='ID-shuffle decoded')
    decoded = pd.DataFrame(decoded_dict)
    shuffled = pd.DataFrame(shuffled_dict)
    data = pd.concat([shuffled, decoded])
    colours = ['#ffffff', '#bdbdbd']

    print('actual:', np.mean(decode_errors[experiment_time]['together']),
          stats.sem(decode_errors[experiment_time]['together']))
    print('shuffle:', np.mean(shuffled_errors[experiment_time]['together']),
          stats.sem(shuffled_errors[experiment_time]['together']))

    plt.figure(figsize=(6, 4))
    flierprops = dict(marker='o', markersize=fliersize, linestyle='none')
    # ax = sns.boxplot(x='shuffled', y='error', data=data, palette=colours, flierprops=flierprops)
    ax = sns.boxplot(x='shuffled', y='error', data=data, flierprops=flierprops)

    edge_colour = '#252525'
    for i, artist in enumerate(ax.artists):
        artist.set_edgecolor(edge_colour)
        artist.set_facecolor(colours[i])

        for j in range(i*6, i*6+6):
            line = ax.lines[j]
            line.set_color(edge_colour)
            line.set_mfc(edge_colour)
            line.set_mec(edge_colour)

    ax.text(-0.05, -0.15, 'N = ' + str(len(decode_errors)),
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color='k', fontsize=10)

    ax.set(xlabel=' ', ylabel="Error (cm)")

    sns.despine()
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, transparent=transparent)
        plt.close()
    else:
        plt.show()


def plot_decoded_session_errors(decode_errors, shuffled_errors, n_sessions, fliersize=1, savepath=None, transparent=False):
    """Plots boxplot distance between decoded and actual position for decoded and shuffled_id

    Parameters
    ----------
    decode_errors: list
    shuffled_errors: list
    n_sessions: int
    fliersize: int
    savepath : str or None
        Location and filename for the saved plot.

    """
    decoded_dict = dict(error=decode_errors, shuffled='Decoded')
    shuffled_dict = dict(error=shuffled_errors, shuffled='ID-shuffle decoded')
    decoded = pd.DataFrame(decoded_dict)
    shuffled = pd.DataFrame(shuffled_dict)
    data = pd.concat([shuffled, decoded])
    colours = ['#ffffff', '#bdbdbd']

    print('actual:', np.mean(decode_errors), stats.sem(decode_errors))
    print('shuffle:', np.mean(shuffled_errors), stats.sem(shuffled_errors))

    plt.figure(figsize=(6, 4))
    flierprops = dict(marker='o', markersize=fliersize, linestyle='none')
    # ax = sns.boxplot(x='shuffled', y='error', data=data, palette=colours, flierprops=flierprops)
    ax = sns.boxplot(x='shuffled', y='error', data=data, flierprops=flierprops)

    edge_colour = '#252525'
    for i, artist in enumerate(ax.artists):
        artist.set_edgecolor(edge_colour)
        artist.set_facecolor(colours[i])

        for j in range(i*6, i*6+6):
            line = ax.lines[j]
            line.set_color(edge_colour)
            line.set_mfc(edge_colour)
            line.set_mec(edge_colour)

    ax.text(0.9, 1., 'n_sessions = ' + str(n_sessions),
            verticalalignment='bottom',
            horizontalalignment='right',
            transform=ax.transAxes,
            color='k', fontsize=10)

    ax.set(xlabel=' ', ylabel="Error (cm)")

    sns.despine()
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, transparent=transparent)
        plt.close()
    else:
        plt.show()


# Seaborn specific properties for combined phases
def plot_v3(data, exp_labels, errors=True):
    fig = sns.FacetGrid(data, col='trajectory', col_order=['U', 'Shortcut', 'Novel'], sharex=False)

    if errors:
        fig.map(sns.barplot, 'trajectory', 'total', 'exp_time',  hue_order=[exp_labels[0], exp_labels[1]])
    else:
        fig.map(sns.barplot, 'trajectory', 'total', 'exp_time',  hue_order=[exp_labels[0], exp_labels[1]], ci=None)
    axes = np.array(fig.axes.flat)

    return plt.gcf(), axes


def set_labels(fig, axes, exp_labels, ylabel):
    labels = ['U', 'Shortcut', 'Novel']

    for i, ax in enumerate(axes):
        ax.set_xticks([-.2, .2])
        ax.set_xticklabels([exp_labels[0], exp_labels[1]])
        ax.set_xlabel(labels[i])
        ax.set_ylabel('')
        ax.set_title('')
    # plt.ylim(0, 0.062)

    axes.flat[0].set_ylabel(ylabel)

    sns.despine(ax=axes[1], left=True)
    sns.despine(ax=axes[2], left=True)


def set_style():
    # sns.set(font='serif')
    # plt.style.use(['seaborn-white', 'seaborn-paper'])
    plt.style.use(['seaborn-white', 'seaborn-poster'])


def color_bars(axes):
    colors = sns.color_palette('colorblind')
    for i in range(3):
        p1, p2 = axes[i].patches

        p1.set_color(colors[i])
        p1.set_edgecolor('k')

        p2.set_color(colors[i])
        p2.set_edgecolor('k')
        # p2.set_hatch('//')


def set_size(fig):
    fig.set_size_inches(9., 6.)
    plt.tight_layout()


def plot_decoded_compare(decodes, ylabel='Proportion', figsize=(8, 5), savepath=None, transparent=False, labels=None):
    """Plots barplot comparing decoded during experiment phases

    Parameters
    ----------
    decodes: list
        Of OrderedDict with experiment_time as keys, each a dict.
        The keys of that dict are u, shortcut, novel, other, each a nept.Position object.
    ylabel: str
    savepath : str or None
        Location and filename for the saved plot.

    """
    if labels is None:
        labels = decodes[0].keys()

    decode = OrderedDict()
    for experimental_time in decodes[0].keys():
        decode[experimental_time] = dict(u=[], shortcut=[], novel=[])

    for session in decodes:
        for experimental_time in session.keys():
            for trajectory in ['u', 'shortcut', 'novel']:
                decode[experimental_time][trajectory].append(session[experimental_time][trajectory])

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey='all', figsize=figsize)

    ind = np.arange(1)
    width = 0.45
    xtick_loc = []
    colours = dict(u='#0072b2', shortcut='#009e73', novel='#d55e00')

    for ax, trajectory in zip([ax1, ax2, ax3], ['u', 'shortcut', 'novel']):
        count = 0
        for key in decode:
            ax.bar(ind + (count * width), np.mean(decode[key][trajectory]), width, color=colours[trajectory],
                   yerr=stats.sem(decode[key][trajectory]), ecolor='k', edgecolor='k')
            xtick_loc.append(ind + (count * width))
            count += 1

    for ax in [ax2, ax3]:
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', which='both', length=0)


    for ax, trajectory in zip([ax1, ax2, ax3], ['U', 'Shortcut', 'Dead-end']):
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlabel(trajectory)
        ax.set_xticks(xtick_loc)
        ax.set_xticklabels(labels, rotation='vertical')
        ax.xaxis.labelpad = 15
        ax.xaxis.set_ticks_position('bottom')

    ax1.set_ylabel(ylabel)
    ax1.yaxis.set_ticks_position('left')

    ax1.text(-0.35, -0.15, 'N = ' + str(len(decodes)),
             verticalalignment='bottom',
             horizontalalignment='right',
             color='k', fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.08)

    if savepath is not None:
        plt.savefig(savepath, transparent=transparent)
        plt.close()
    else:
        plt.show()


def plot_cooccur_weighted_pauses(cooccur_1, epochs_1, cooccur_2, epochs_2, labels, prob, ylabel, savepath=None):
    """Plots barplot comparing cooccur probabilities during two phases.

    Parameters
    ----------
    cooccur_1: dict
        With u, shortcut, novel, other as keys, each a nept.Position object.
    cooccur_2: dict
        With u, shortcut, novel, other as keys, each a nept.Position object.
    labels: list of str
    prob: str
        One of expected, observed, active, shuffle, zscore
    ylabel=str

    savepath : str or None
        Location and filename for the saved plot.

    """
    if prob not in ['expected', 'observed', 'active', 'shuffle', 'zscore']:
        raise ValueError("prob must be one of expected, observed, active, shuffle or zscore")

    weighted_mean1 = dict()
    weighted_sem1 = dict()
    for key in cooccur_1:
        epochs_1 = np.array(epochs_1)
        cooccur_1[key][prob] = np.array(cooccur_1[key][prob])
        total_weight1 = np.sum(epochs_1)
        weighted_mean1[key] = np.sum(cooccur_1[key][prob]) / total_weight1
        observations1 = cooccur_1[key][prob] / epochs_1
        weighted_sem1[key] = np.sqrt(
                             np.sum(epochs_1**2 * (observations1 - weighted_mean1[key])**2)) / total_weight1

    weighted_mean2 = dict()
    weighted_sem2 = dict()
    for key in cooccur_2:
        epochs_2 = np.array(epochs_2)
        cooccur_2[key][prob] = np.array(cooccur_2[key][prob])
        total_weight2 = np.sum(epochs_2)
        weighted_mean2[key] = np.sum(cooccur_2[key][prob]) / total_weight2
        observations2 = cooccur_2[key][prob] / epochs_2
        weighted_sem2[key] = np.sqrt(
            np.sum(epochs_2 ** 2 * (observations2 - weighted_mean2[key]) ** 2)) / total_weight2

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True, figsize=(4.5, 2.5))

    ind = np.arange(1)
    width = 0.5
    colours = dict(u='#0072b2', shortcut='#009e73', novel='#d55e00')

    for ax, trajectory in zip([ax1, ax2, ax3], ['u', 'shortcut', 'novel']):
        ax.bar(ind, weighted_mean1[trajectory], width,
               color=colours[trajectory], yerr=weighted_sem1[trajectory], ecolor='k')
        ax.bar(ind + width, weighted_mean2[trajectory], width,
               color=colours[trajectory], yerr=weighted_sem2[trajectory], ecolor='k')

    ax1.set_ylabel(ylabel)
    ax1.yaxis.set_ticks_position('left')

    for ax in [ax2, ax3]:
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', which='both', length=0)

    for ax, trajectory in zip([ax1, ax2, ax3], ['U', 'Shortcut', 'Novel']):
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlabel(trajectory)
        ax.set_xticks([ind + 0.5 * width, ind + width + 0.5 * width])
        ax.set_xticklabels(labels)
        ax.xaxis.set_ticks_position('bottom')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.08)

    if savepath is not None:
        plt.savefig(savepath, transparent=True)
        plt.close()
    else:
        plt.show()
