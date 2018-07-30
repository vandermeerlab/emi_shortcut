import os
import numpy as np
import pickle
from shapely.geometry import Point, LineString

import nept

from loading_data import get_data
from utils_maze import spikes_by_position

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


def get_only_tuning_curves(position, spikes, xedges, yedges, epoch_of_interest):
    sliced_position = position.time_slice(epoch_of_interest.start, epoch_of_interest.stop)
    sliced_spikes = [spiketrain.time_slice(epoch_of_interest.start, epoch_of_interest.stop) for spiketrain in spikes]

    # Limit position and spikes to only running times
    run_epoch = nept.run_threshold(sliced_position, thresh=10., t_smooth=0.8)
    run_position = sliced_position[run_epoch]
    tuning_spikes = [spiketrain.time_slice(run_epoch.starts, run_epoch.stops) for spiketrain in sliced_spikes]

    tuning_curves = nept.tuning_curve_2d(run_position, tuning_spikes, xedges, yedges, occupied_thresh=0.5, gaussian_std=0.3)

    return tuning_curves


def get_tuning_curves(info, sliced_position, sliced_spikes, xedges, yedges, speed_limit=10.0, t_smooth=0.8,
                      min_n_spikes=100, phase_id=None, trial_times=None, trial_number=None, cache=True):
    """

    Parameters
    ----------
    info: module
    sliced_position: nept.Position
    speed_limit: float
    min_n_spikes: int or None
    phase_id: str
    trial_times: nept.Epoch or None
    trial_number: int or None
    cache: bool

    Returns
    -------
    neurons: nept.Neurons

    """
    print('generating tuning curves for', info.session_id)

    if trial_times is not None and trial_times.n_epochs != 1:
        raise AssertionError("trial_times must only contain one epoch (start, stop)")

    if trial_number is None:
        trial_number = ""

    if trial_times is None:
        trial_times = nept.Epoch([], [])

    phase1 = nept.Epoch([info.task_times['phase1'].start, info.task_times['phase1'].stop])
    phase2 = nept.Epoch([info.task_times['phase2'].start, info.task_times['phase2'].stop])
    phase3 = nept.Epoch([info.task_times['phase3'].start, info.task_times['phase3'].stop])

    if phase_id is None:
        track_starts = []
        track_stops = []
        for phase in [phase1, phase2, phase3]:
            if phase.overlaps(trial_times).durations.size > 0:
                if trial_times.start < phase.start:
                    phase = nept.Epoch([trial_times.stop, phase.stop])
                elif trial_times.stop > phase.stop:
                    phase = nept.Epoch([phase.start, trial_times.start])
                else:
                    phase = nept.Epoch([[phase.start, trial_times.stop], [trial_times.start, phase.stop]])
            track_starts.extend(phase.starts)
            track_stops.extend(phase.stops)
        filename = info.session_id + '_neurons_all-phases' + str(trial_number) + '.pkl'
    else:
        phase = nept.Epoch([info.task_times[phase_id].start, info.task_times[phase_id].stop])

        track_starts = []
        track_stops = []
        if phase.overlaps(trial_times).durations.size > 0:
            if trial_times.start < phase.start:
                phase = nept.Epoch([trial_times.stop, phase.stop])
            elif trial_times.stop > phase.stop:
                phase = nept.Epoch([phase.start, trial_times.start])
            else:
                phase = nept.Epoch([[phase.start, trial_times.stop], [trial_times.start, phase.stop]])

            track_starts.extend(phase.starts)
            track_stops.extend(phase.stops)
        filename = info.session_id + '_neurons' + str(trial_number) + '.pkl'

    # limit position to only times when the subject is moving faster than a certain threshold
    run_epoch = nept.run_threshold(sliced_position, thresh=speed_limit, t_smooth=t_smooth)
    run_position = sliced_position[run_epoch]

    track_spikes = [spiketrain.time_slice(run_epoch.starts, run_epoch.stops) for spiketrain in sliced_spikes]

    filtered_spikes = []
    tuning_spikes = []
    if min_n_spikes is not None:
        for neuron, neuron_all in zip(track_spikes, sliced_spikes):
            if len(neuron.time) > min_n_spikes:
                tuning_spikes.append(neuron)
                filtered_spikes.append(neuron_all)
    else:
        tuning_spikes = track_spikes
        filtered_spikes = sliced_spikes

    tuning_curves = nept.tuning_curve_2d(run_position, tuning_spikes, xedges, yedges,
                                         occupied_thresh=0.5, gaussian_std=0.3)

    tuning_curves[np.isnan(tuning_curves)] = 0.

    neurons = nept.Neurons(np.array(filtered_spikes), tuning_curves)

    if cache:
        pickled_tc = os.path.join(pickle_filepath, filename)

        with open(pickled_tc, 'wb') as fileobj:
            pickle.dump(neurons, fileobj)

    return neurons


if __name__ == "__main__":
    from run import spike_sorted_infos, info
    infos = spike_sorted_infos
    # infos = [info.r066d1]

    if 1:
        for info in infos:
            events, position, spikes, lfp, lfp_theta = get_data(info)
            xedges, yedges = nept.get_xyedges(position, binsize=8)
            get_tuning_curves(info, position, spikes, xedges, yedges,
                              min_n_spikes=None, trial_times=None, trial_number=None, cache=True)
    if 0:
        for info in infos:
            get_tuning_curves(info, use_all_tracks=True)
