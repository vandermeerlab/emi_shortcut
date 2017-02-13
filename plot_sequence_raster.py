import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from shapely.geometry import Point, LineString
import scalebar
import vdmlab as vdm

from loading_data import get_data
from utils_maze import find_zones
from utils_fields import categorize_fields
from analyze_tuning_curves import get_odd_firing_idx

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'sequence')

sns.set_style('white')
sns.set_style('ticks')


def plot_sequence(ordered_spikes, start_time, stop_time, ms_fraction=132, lfp=None, position=None, savepath=None):
    rows = len(ordered_spikes)
    add_rows = int(rows / 8)

    ms = ms_fraction / rows
    mew = 0.7
    spike_loc = 1

    fig = plt.figure(figsize=(7, 6))
    ax1 = plt.subplot2grid((rows+add_rows, 1), (0, 0), rowspan=rows)


    for idx, neuron_spikes in enumerate(ordered_spikes):
        ax1.plot(neuron_spikes.time, np.ones(len(neuron_spikes.time))+(idx*spike_loc)-1, '|',
                 color='k', ms=ms, mew=mew)
    ax1.set_xticks([])
    ax1.set_xlim([start_time, stop_time])
    ax1.set_ylim([-0.5, len(ordered_spikes)*spike_loc])

    if lfp is not None:
        ax2 = plt.subplot2grid((rows+add_rows, 1), (rows, 0), rowspan=add_rows, sharex=ax1)
        start_idx = vdm.find_nearest_idx(lfp.time, start_time)
        stop_idx = vdm.find_nearest_idx(lfp.time, stop_time)
        ax2.plot(lfp.time[start_idx:stop_idx], lfp.data[start_idx:stop_idx], '#3288bd', lw=0.3)
        ax2.set_xticks([])
        ax2.set_xlim([start_time, stop_time])
        ax2.set_yticks([])

        scalebar.add_scalebar(ax2, matchy=False, bbox_transform=fig.transFigure,
                              bbox_to_anchor=(0.9, 0.05), units='ms')

    elif position is not None:
        ax2 = plt.subplot2grid((rows+add_rows, 1), (rows, 0), rowspan=add_rows, sharex=ax1)
        start_idx = vdm.find_nearest_idx(position.time, start_time)
        stop_idx = vdm.find_nearest_idx(position.time, stop_time)
        ax2.plot(position.time[start_idx:stop_idx], position.x[start_idx:stop_idx], '#9970ab', lw=1)
        ax2.plot(position.time[start_idx:stop_idx], position.y[start_idx:stop_idx], '#5aae61', lw=1)
        ax2.set_xticks([])
        ax2.set_xlim([start_time, stop_time])
        ax2.set_yticks([])

        scalebar.add_scalebar(ax2, matchy=False, bbox_transform=fig.transFigure,
                              bbox_to_anchor=(0.9, 0.05), units='ms')

    else:
        scalebar.add_scalebar(ax1, matchy=False, bbox_transform=fig.transFigure,
                              bbox_to_anchor=(0.9, 0.08), units='s')

    sns.despine(bottom=True)
    plt.tight_layout(h_pad=0.003)

    if savepath is not None:
        plt.savefig(savepath, bbox_inches='tight', transparent=True)
        plt.close()
    else:
        plt.show()


def analyze(info, output_filepath=output_filepath, savefig=True):
    print(info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)

    times = info.task_times['phase3']

    sliced_spikes = [spiketrain.time_slice(times.start, times.stop) for spiketrain in spikes]
    sliced_pos = position.time_slice(times.start, times.stop)

    binsize = 3
    xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
    yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)

    neurons_filename = info.session_id + '_neurons.pkl'
    pickled_neurons = os.path.join(pickle_filepath, neurons_filename)
    with open(pickled_neurons, 'rb') as fileobj:
        neurons = pickle.load(fileobj)

    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.
    xy_centers = vdm.cartesian(xcenters, ycenters)

    zones = find_zones(info, remove_feeder=False, expand_by=4)

    field_thresh = 1.0
    fields_tunings = categorize_fields(neurons.tuning_curves, zones, xedges, yedges, field_thresh=field_thresh)

    u_line = LineString(info.u_trajectory)
    shortcut_line = LineString(info.shortcut_trajectory)
    novel_line = LineString(info.novel_trajectory)

    u_dist = []
    for neuron in fields_tunings['u']:
        yy = ycenters[np.where(fields_tunings['u'][neuron] == fields_tunings['u'][neuron].max())[0][0]]
        xx = xcenters[np.where(fields_tunings['u'][neuron] == fields_tunings['u'][neuron].max())[1][0]]

        pt = Point(xx, yy)
        if zones['u'].contains(pt):
            u_dist.append((u_line.project(pt), neuron))

    ordered_dist_u = sorted(u_dist, key=lambda x:x[0])
    sort_idx = []
    for neuron in ordered_dist_u:
        sort_idx.append(neuron[1])

    sort_spikes = []
    sort_tuning_curves = []
    for neuron in sort_idx:
        sort_tuning_curves.append(fields_tunings['u'][neuron])
        sort_spikes.append(spikes[neuron])


    odd_firing_idx = get_odd_firing_idx(sort_tuning_curves, max_mean_firing=2)
    ordered_spikes = []
    ordered_fields =[]
    for i, neuron in enumerate(sort_spikes):
        if i not in odd_firing_idx:
            ordered_spikes.append(neuron)
            ordered_fields.append(sort_tuning_curves[i])

    for trajectory in ['u', 'shortcut']:
        for time in ['run', 'swr']:
            for i, (start, stop) in enumerate(zip(info.sequence[trajectory][time].starts,
                                                  info.sequence[trajectory][time].stops)):
                savepath = os.path.join(output_filepath, info.session_id + '_' + time + '-' + trajectory + str(i) + '.pdf')
                if savefig:
                    plot_sequence(ordered_spikes, lfp, start, stop, savepath)
                else:
                    plot_sequence(ordered_spikes, lfp, start, stop)


if __name__ == "__main__":
    from run import spike_sorted_infos
    infos = spike_sorted_infos

    for info in infos:
        analyze(info)
