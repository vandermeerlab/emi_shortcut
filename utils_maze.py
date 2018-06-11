import numpy as np
from shapely.geometry import Point, LineString

import nept


def get_trial_idx(low_priority, mid_priority, high_priority, feeder1_times, feeder2_times, phase_stop):
    """Gets the indices associated with each behavioral trial.

    Parameters
    ----------
    low_priority : np.array
        Spike_pos times. This track segment is considered last. Eg. U for the shortcut analysis.
    mid_priority : np.array
        Spike_pos times. This track segment is considered second. Eg. Shortcut for the shortcut analysis.
    high_priority : np.array
        Spike_pos times. This track segment is considered first. Eg. Novel for the shortcut analysis.
    feeder1_times : list
        List of times (floats) the photobeam was broken for feeder1.
    feeder2_times : list
        List of times (floats) the photobeam was broken for feeder1.
    phase_stop : float
        Time (float) of the end of the phase.

    Returns
    -------
    trials_idx : dict
        With start_trials, stop_trials, u, shortcut, novel keys that are lists of indices.

    """
    start_trials = []
    stop_trials = []

    high_priority_time = []
    mid_priority_time = []
    low_priority_time = []

    f1_idx = 0
    f2_idx = 0

    while f1_idx < len(feeder1_times) and f2_idx < len(feeder2_times):
        if f1_idx == len(feeder1_times):
            start_trial = feeder2_times[f2_idx]
            stop_trial = phase_stop
        elif f2_idx == len(feeder2_times):
            start_trial = feeder1_times[f1_idx]
            stop_trial = phase_stop
        else:
            start_trial = min(feeder1_times[f1_idx], feeder2_times[f2_idx])
            if start_trial in feeder1_times:
                f1_idx += 1
                stop_trial = feeder2_times[f2_idx]
            elif start_trial in feeder2_times:
                f2_idx += 1
                stop_trial = feeder1_times[f1_idx]
        start_trials.append(start_trial)
        stop_trials.append(stop_trial)

        for element in high_priority:
            if np.logical_and(start_trial <= element, element < stop_trial):
                high_priority_time.append(start_trial)
                break
        if start_trial not in high_priority_time:
            for element in mid_priority:
                if np.logical_and(start_trial <= element, element < stop_trial):
                    mid_priority_time.append(start_trial)
                    break
        if start_trial not in high_priority_time and start_trial not in mid_priority_time:
            for element in low_priority:
                if np.logical_and(start_trial <= element, element < stop_trial):
                    low_priority_time.append(start_trial)
                    break

    high_priority_trials = []
    mid_priority_trials = []
    low_priority_trials = []

    for trial in high_priority_time:
        high_priority_trials.append((nept.find_nearest_idx(np.array(start_trials), trial), 'novel'))
    for trial in mid_priority_time:
        mid_priority_trials.append((nept.find_nearest_idx(np.array(start_trials), trial), 'shortcut'))
    for trial in low_priority_time:
        low_priority_trials.append((nept.find_nearest_idx(np.array(start_trials), trial), 'u'))

    trials_idx = dict()
    trials_idx['novel'] = high_priority_trials
    trials_idx['shortcut'] = mid_priority_trials
    trials_idx['u'] = low_priority_trials

    trials_epochs = nept.Epoch([start_trials, stop_trials])

    return trials_idx, trials_epochs


def spikes_by_position(spikes, zone, position):
    """Finds the spikes that occur while the animal is in certain positions.

    Parameters
    ----------
    spikes : list
        Contains nept.SpikeTrain for each neuron
    zone : dict
        With 'ushort', 'u', 'novel', 'uped', 'unovel', 'pedestal',
        'novelped', 'shortcut', 'shortped' keys.
        Each value is a unique Shapely Polygon object.
    position : nept.Position

    Returns
    -------
    path_spikes : dict
        With u, shortcut, novel, other keys. Each value is a list of nept.SpikeTrain.

    """
    counter = 0
    path_spikes = dict(pedestal=[], u=[], shortcut=[], novel=[], other=[])

    for spiketrain in spikes:
        neuron_spikes = dict(pedestal=[], u=[], shortcut=[], novel=[], other=[])
        for spike in spiketrain.time:
            pos_idx = nept.find_nearest_idx(position.time, spike)
            point = Point([position.x[pos_idx], position.y[pos_idx]])
            if zone['pedestal'].contains(point) or zone['uped'].contains(point) or zone['shortped'].contains(point) or zone['novelped'].contains(point):
                neuron_spikes['pedestal'].append(np.asscalar(spike))
                continue
            elif zone['u'].contains(point) or zone['ushort'].contains(point) or zone['unovel'].contains(point):
                neuron_spikes['u'].append(np.asscalar(spike))
                continue
            elif zone['shortcut'].contains(point):
                neuron_spikes['shortcut'].append(np.asscalar(spike))
                continue
            elif zone['novel'].contains(point):
                neuron_spikes['novel'].append(np.asscalar(spike))
                continue
            else:
                neuron_spikes['other'].append(np.asscalar(spike))

        if len(neuron_spikes['u']) > 1:
            path_spikes['u'].append(nept.SpikeTrain(np.array(neuron_spikes['u']), spiketrain.label))
        if len(neuron_spikes['shortcut']) > 1:
            path_spikes['shortcut'].append(nept.SpikeTrain(np.array(neuron_spikes['shortcut']), spiketrain.label))
        if len(neuron_spikes['novel']) > 1:
            path_spikes['novel'].append(nept.SpikeTrain(np.array(neuron_spikes['novel']), spiketrain.label))
        if len(neuron_spikes['other']) > 1:
            path_spikes['other'].append(nept.SpikeTrain(np.array(neuron_spikes['other']), spiketrain.label))

        counter += 1
        print(str(counter) + ' of ' + str(len(spikes)) + ' neurons completed!')

    return path_spikes


def get_zones(info, position, expand_by=6):
    """Finds the spikes that occur while the animal is in certain positions.

    Parameters
    ----------
    info : module
        Module with session-specific information
    position : nept.Position
        Must be a 2D position.

    Returns
    -------
    spike_pos : dict
        With u, shortcut, novel, other keys that are each dicts with x, y, time keys

    """
    # Here I define the ideal trajectories in cm that I project onto
    # to make the 1D linear position.
    u_line = LineString(info.u_trajectory)
    shortcut_line = LineString(info.shortcut_trajectory)
    novel_line = LineString(info.novel_trajectory)

    u_start = Point(info.u_trajectory[0])
    u_stop = Point(info.u_trajectory[-1])
    shortcut_start = Point(info.shortcut_trajectory[0])
    shortcut_stop = Point(info.shortcut_trajectory[-1])
    novel_start = Point(info.novel_trajectory[0])
    novel_stop = Point(info.novel_trajectory[-1])

    zones = dict()
    zones['u'] = nept.expand_line(u_start, u_stop, u_line, expand_by)
    zones['shortcut'] = nept.expand_line(shortcut_start, shortcut_stop, shortcut_line, expand_by)
    zones['novel'] = nept.expand_line(novel_start, novel_stop, novel_line, expand_by)
    zones['ushort'] = zones['u'].intersection(zones['shortcut'])
    zones['unovel'] = zones['u'].intersection(zones['novel'])

    u_idx = []
    shortcut_idx = []
    novel_idx = []
    other_idx = []
    for pos_idx in list(range(len(position.time))):
        point = Point([position.x[pos_idx], position.y[pos_idx]])
        if zones['u'].contains(point) or zones['ushort'].contains(point) or zones['unovel'].contains(point):
            u_idx.append(pos_idx)
        elif zones['shortcut'].contains(point):
            shortcut_idx.append(pos_idx)
        elif zones['novel'].contains(point):
            novel_idx.append(pos_idx)
        else:
            other_idx.append(pos_idx)

    path_pos = dict()
    path_pos['u'] = position[u_idx]
    path_pos['shortcut'] = position[shortcut_idx]
    path_pos['novel'] = position[novel_idx]
    path_pos['other'] = position[other_idx]

    return path_pos


def expand_line(start_pt, stop_pt, line, expand_by):
    """Expands shapely line into a zone.

    Parameters
    ----------
    start_pt : shapely.Point
    stop_pt : shapely.Point
    line : shapely.LineString
    expand_by : int or float

    Returns
    -------
    zone : shapely.Polygon

    """
    line_expanded = line.buffer(expand_by)
    zone = start_pt.union(line_expanded).union(stop_pt)

    return zone


def find_zones(info, remove_feeder, expand_by=6):
    """Finds zones from ideal trajectories.

    Parameters
    ----------
    info : shortcut module
    remove_feeder: boolean
    expand_by : int or float
        Amount to expand the line.

    Returns
    -------
    zone : dict
        With shapely.Polygon as values.
        Keys are u, shortcut, novel, ushort, unovel, uped, shortped,
        novelped, pedestal.

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
    feeder1_center = Point(info.path_pts['feeder1'][0], info.path_pts['feeder1'][1])
    feeder1 = feeder1_center.buffer(expand_by * 1.2)
    feeder2_center = Point(info.path_pts['feeder2'][0], info.path_pts['feeder2'][1])
    feeder2 = feeder2_center.buffer(expand_by * 1.2)

    zone_u = expand_line(u_start, u_stop, u_line, expand_by)
    zone_shortcut = expand_line(shortcut_start, shortcut_stop, shortcut_line, expand_by)
    zone_novel = expand_line(novel_start, novel_stop, novel_line, expand_by)

    zone = dict()
    zone['u'] = zone_u
    zone['u'] = zone['u'].difference(pedestal)
    zone['shortcut'] = zone_shortcut.difference(zone_u)
    zone['shortcut'] = zone['shortcut'].difference(zone_novel)
    zone['shortcut'] = zone['shortcut'].difference(pedestal)
    zone['novel'] = zone_novel.difference(zone_u)
    zone['novel'] = zone['novel'].difference(pedestal)
    zone['pedestal'] = pedestal

    if remove_feeder:
        for feeder in [feeder1, feeder2]:
            zone['u'] = zone['u'].difference(feeder)
            zone['shortcut'] = zone['shortcut'].difference(feeder)
            zone['novel'] = zone['novel'].difference(feeder)
            zone['pedestal'] = zone['pedestal'].difference(feeder)

    return zone


def trajectory_fields(tuning_curves, spikes, zone, xedges, yedges, field_thresh):
    """Finds track tuning curves that have firing above field_thresh.

    Parameters
    ----------
    tuning_curves : list of np.arrays
    spikes: list of nept.SpikeTrain objects
    zone : shapely.Polygon
    xedges : np.array
    yedges : np.array
    field_thresh : float
        Threshold (in Hz) that determines whether the neuron has a field.

    Returns
    -------
    fields_tc : dict
        With u, shortcut, novel, pedestal as keys. Values are np.arrays.
    """
    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.

    xy_centers = nept.cartesian(xcenters, ycenters)

    in_u = []
    in_shortcut = []
    in_novel = []
    in_pedestal = []

    fields_tc = dict(u=[], shortcut=[], novel=[], pedestal=[])
    fields_neuron = dict(u=[], shortcut=[], novel=[], pedestal=[])
    for i, neuron_tc in enumerate(tuning_curves):
        field_idx = neuron_tc.flatten() > field_thresh
        field = xy_centers[field_idx]
        for pt in field:
            point = Point([pt[0], pt[1]])
            if zone['u'].contains(point) or zone['ushort'].contains(point) or zone['unovel'].contains(point):
                if i not in in_u:
                    in_u.append(i)
                    fields_tc['u'].append(neuron_tc)
                    fields_neuron['u'].append(spikes[i])
            if zone['shortcut'].contains(point) or zone['shortped'].contains(point):
                if i not in in_shortcut:
                    in_shortcut.append(i)
                    fields_tc['shortcut'].append(neuron_tc)
                    fields_neuron['shortcut'].append(spikes[i])
            if zone['novel'].contains(point) or zone['novelped'].contains(point):
                if i not in in_novel:
                    in_novel.append(i)
                    fields_tc['novel'].append(neuron_tc)
                    fields_neuron['novel'].append(spikes[i])
            if zone['pedestal'].contains(point):
                if i not in in_pedestal:
                    in_pedestal.append(i)
                    fields_tc['pedestal'].append(neuron_tc)
                    fields_neuron['pedestal'].append(spikes[i])

    return fields_tc, fields_neuron


def get_xyedges(position, binsize=3):
    """Gets edges based on position min and max.

    Parameters
    ----------
    position: 2D nept.Position
    binsize: int

    Returns
    -------
    xedges: np.array
    yedges: np.array

    """
    xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
    yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)

    return xedges, yedges


def speed_threshold(position, t_smooth=0.5, speed_limit=4., rest=False):
    """Finds times where position is above a certain speed threshold

    Parameters
    ----------
    position: nept.Position
    t_smooth: float
    speed_limit: float

    Returns
    -------
    epoch_run: nept.Epoch

    """
    speed = position.speed(t_smooth)

    idx = np.where(np.diff(np.squeeze(speed.data) > speed_limit / 10.))[0]

    if rest:
        t_start = position.time[idx[1::2]]
        t_stop = position.time[idx[2::2]]
    else:
        t_start = position.time[idx[::2]]
        t_stop = position.time[idx[1::2]]

    if len(t_start) != len(t_stop):
        assert len(t_start) - len(t_stop) == 1
        t_stop = np.hstack([t_stop, position.time[-1]])

    return nept.Epoch(np.vstack((t_start, t_stop)))


def get_trials(events, phase_epoch):
    feeder_events = np.sort(np.append(events['feeder1'], events['feeder2']))
    feeder_events = feeder_events[np.where((phase_epoch.start < feeder_events)*(feeder_events < phase_epoch.stop))[0]]

    return nept.Epoch([feeder_events[:-1], feeder_events[1:]])


def convert_to_cm(path_pts, xy_conversion):
    for key in path_pts:
        path_pts[key][0] = path_pts[key][0] / xy_conversion[0]
        path_pts[key][1] = path_pts[key][1] / xy_conversion[1]
    return path_pts
