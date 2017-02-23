import os
import numpy as np
import pickle
from shapely.geometry import Point, LineString

import nept

from loading_data import get_data
from utils_maze import spikes_by_position, speed_threshold

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')

def expand_line(start_pt, stop_pt, line, expand_by):
    """Expands shapely Linestring.

    Parameters
    ----------
    start_pt : shapely.Point
    stop_pt : shapely.Point
    line : shapely.LineString
    expand_by : float
        Amount to expand the line.

    Returns
    -------
    zone : shapely object
    """
    line_expanded = line.buffer(expand_by)
    zone = start_pt.union(line_expanded).union(stop_pt)
    return zone


def find_ideal(info, position, expand_by=6):
    """Finds linear and zones for ideal trajectories.

        Parameters
        ----------
        info : module
            Contains session-specific information.
        position : nept.Position
        expand_by : int or float
            This is how much you wish to expand the line to fit
            the animal's actual movements. Default is set to 6.

        Returns
        -------
        linear : dict
            With u, shortcut, novel keys. Each value is a unique
            shapely.LineString object.
        zone : dict
            With 'ushort', 'u', 'novel', 'uped', 'unovel', 'pedestal',
            'novelped', 'shortcut', 'shortped' keys.
            Each value is a unique shapely.Polygon object.

        """
    u_line = LineString(info.u_trajectory)
    shortcut_line = LineString(info.shortcut_trajectory)
    novel_line = LineString(info.novel_trajectory)

    u_start = Point(info.u_trajectory[0])
    u_stop = Point(info.u_trajectory[-1])
    shortcut_start = Point(info.shortcut_trajectory[0])
    shortcut_stop = Point(info.shortcut_trajectory[-1])
    novel_start = Point(info.novel_trajectory[0])
    novel_stop = Point(info.novel_trajectory[-1])
    pedestal_center = Point(info.path_pts['pedestal'][0], info.path_pts['pedestal'][1])
    pedestal = pedestal_center.buffer(expand_by*2.2)

    zone = dict()
    zone['u'] = expand_line(u_start, u_stop, u_line, expand_by)
    zone['shortcut'] = expand_line(shortcut_start, shortcut_stop, shortcut_line, expand_by)
    zone['novel'] = expand_line(novel_start, novel_stop, novel_line, expand_by)
    zone['ushort'] = zone['u'].intersection(zone['shortcut'])
    zone['unovel'] = zone['u'].intersection(zone['novel'])
    zone['uped'] = zone['u'].intersection(pedestal)
    zone['shortped'] = zone['shortcut'].intersection(pedestal)
    zone['novelped'] = zone['novel'].intersection(pedestal)
    zone['pedestal'] = pedestal

    u_idx = []
    shortcut_idx = []
    novel_idx = []
    other_idx = []
    for pos_idx in range(len(position.time)):
        point = Point([position.x[pos_idx], position.y[pos_idx]])
        if zone['u'].contains(point) or zone['ushort'].contains(point) or zone['unovel'].contains(point):
            u_idx.append(pos_idx)
        elif zone['shortcut'].contains(point) or zone['shortped'].contains(point):
            shortcut_idx.append(pos_idx)
        elif zone['novel'].contains(point) or zone['novelped'].contains(point):
            novel_idx.append(pos_idx)
        else:
            other_idx.append(pos_idx)

    u_pos = position[u_idx]
    shortcut_pos = position[shortcut_idx]
    novel_pos = position[novel_idx]
    other_pos = position[other_idx]

    linear = dict()
    if len(u_pos.time) > 0:
        linear['u'] = u_pos.linearize(u_line, zone['u'])
    else:
        linear['u'] = None
    if len(shortcut_pos.time) > 0:
        linear['shortcut'] = shortcut_pos.linearize(shortcut_line, zone['shortcut'])
    else:
        linear['shortcut'] = None
    if len(novel_pos.time) > 0:
        linear['novel'] = novel_pos.linearize(novel_line, zone['novel'])
    else:
        linear['novel'] = None

    return linear, zone


def get_tc_1d(info, position, spikes, pickled_tc, binsize, expand_by=2, sampling_rate=1/30.):
    """Calls 1D tuning curve.

        Parameters
        ----------
        info : module
            Contains session-specific information.
        position : nept.Position
        spikes : list
            Contains nept.SpikeTrain for each neuron.
        pickled_tc: str
            Absolute location of where tuning_curve.pkl files are saved.

        Returns
        -------
        tc : dict (1D)
            With u, shortcut, novel keys. Each value is a list of list, where
            each inner array represents an individual neuron's tuning curve.
    """
    linear, zone = find_ideal(info, position, expand_by)

    thisdir = os.path.dirname(os.path.realpath(__file__))
    pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
    spike_pos_filename = info.session_id + '_spike_position_phase3.pkl'
    pickled_spike_pos = os.path.join(pickle_filepath, spike_pos_filename)
    if os.path.isfile(pickled_spike_pos):
        with open(pickled_spike_pos, 'rb') as fileobj:
            spike_position = pickle.load(fileobj)
    else:
        spike_position = spikes_by_position(spikes, zone, position)
        with open(pickled_spike_pos, 'wb') as fileobj:
            pickle.dump(spike_position, fileobj)

    tuning_curves = dict()
    if len(linear['u'].x) > 0:
        tuning_curves['u'] = nept.tuning_curve(linear['u'], spike_position['u'], binsize)
    else:
        tuning_curves['u'] = None
    if len(linear['shortcut'].x) > 0:
        tuning_curves['shortcut'] = nept.tuning_curve(linear['shortcut'], spike_position['shortcut'], binsize)
    else:
        tuning_curves['shortcut'] = None
    if len(linear['novel'].x) > 0:
        tuning_curves['novel'] = nept.tuning_curve(linear['novel'], spike_position['novel'], binsize)
    else:
        tuning_curves['novel'] = None

    with open(pickled_tc, 'wb') as fileobj:
        pickle.dump(tuning_curves, fileobj)

    return tuning_curves


def get_odd_firing_idx(tuning_curve, max_mean_firing):
    """Find indices where neuron is firing too much to be considered a place cell

    Parameters
    ----------
    tuning_curve :
    max_mean_firing : int or float
        A neuron with a max mean firing above this level is considered to have odd
        firing and it's index will be added to the odd_firing_idx.

    Returns
    -------
    odd_firing_idx : list of ints
        Where each int is an index into the full list of neurons.

        """
    odd_firing_idx = []
    for idx in range(len(tuning_curve)):
        if (np.mean(tuning_curve[idx]) > max_mean_firing):
            odd_firing_idx.append(idx)
    return odd_firing_idx


def get_outputs(infos):
    outputs = []
    for info in infos:
        outputs.append(os.path.join(pickle_filepath, info.session_id + '_tuning-curve.pkl'))
    return outputs


def get_outputs_all(infos):
    outputs = []
    for info in infos:
        outputs.append(os.path.join(pickle_filepath, info.session_id + '_tuning-curve_all-phases.pkl'))
    return outputs


def analyze(info, speed_limit=0.4, min_n_spikes=100, use_all_tracks=False):
    print('tuning curves:', info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = nept.get_xyedges(position)

    if use_all_tracks:
        track_starts = [info.task_times['phase1'].start,
                    info.task_times['phase2'].start,
                    info.task_times['phase3'].start]
        track_stops = [info.task_times['phase1'].stop,
                       info.task_times['phase2'].stop,
                       info.task_times['phase3'].stop]
        track_position = position.time_slices(track_starts, track_stops)

        filename = info.session_id + '_neurons_all-phases.pkl'
    else:
        track_starts = [info.task_times['phase3'].start]
        track_stops = [info.task_times['phase3'].stop]
        track_position = position.time_slices(track_starts, track_stops)

        filename = info.session_id + '_neurons.pkl'

    run_position = speed_threshold(track_position, speed_limit=speed_limit)

    track_spikes = [spiketrain.time_slices(track_starts, track_stops) for spiketrain in spikes]

    filtered_spikes = []
    tuning_spikes = []
    for neuron, neuron_all in zip(track_spikes, spikes):
        if len(neuron.time) > min_n_spikes:
            tuning_spikes.append(neuron)
            filtered_spikes.append(neuron_all)

    tuning_curves = nept.tuning_curve_2d(run_position, np.array(tuning_spikes),
                                         xedges, yedges, occupied_thresh=0.2, gaussian_sigma=0.1)

    neurons = nept.Neurons(np.array(filtered_spikes), tuning_curves)

    pickled_tc = os.path.join(pickle_filepath, filename)

    with open(pickled_tc, 'wb') as fileobj:
        pickle.dump(neurons, fileobj)

    return neurons


if __name__ == "__main__":
    from run import spike_sorted_infos, info
    infos = spike_sorted_infos
    # infos = [info.r066d3]

    if 1:
        for info in infos:
            analyze(info)
    if 1:
        for info in infos:
            analyze(info, use_all_tracks=True)
