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
        high_priority_trials.append(nept.find_nearest_idx(np.array(start_trials), trial))
    for trial in mid_priority_time:
        mid_priority_trials.append(nept.find_nearest_idx(np.array(start_trials), trial))
    for trial in low_priority_time:
        low_priority_trials.append(nept.find_nearest_idx(np.array(start_trials), trial))

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


def get_trials(events, phase_epoch, first_trial=False):
    feeder_events = np.sort(np.append(events['feeder1'], events['feeder2']))
    feeder_events = feeder_events[np.where((phase_epoch.start < feeder_events)*(feeder_events < phase_epoch.stop))[0]]

    starts = feeder_events[:-1]
    stops = feeder_events[1:]

    # Insert first trial as phase start to first feeder firing during that phase
    if first_trial:
        starts = np.insert(starts, 0, phase_epoch.start)
        stops = np.insert(stops, 0, feeder_events[0])

    return nept.Epoch([starts, stops])


def convert_to_cm(path_pts, xy_conversion):
    for key in path_pts:
        path_pts[key][0] = path_pts[key][0] / xy_conversion[0]
        path_pts[key][1] = path_pts[key][1] / xy_conversion[1]
    return path_pts


def align_to_event(analogsignal, event, t_before, t_after):
    idx = nept.find_nearest_idx(analogsignal.time, event)
    event_of_interest = analogsignal.time[idx]

    sliced = analogsignal.time_slice(event_of_interest - t_before, event_of_interest + t_after)

    time = sliced.time - event_of_interest
    data = np.squeeze(sliced.data)

    return nept.AnalogSignal(data, time)


def get_bin_centers(info):
    xcenters = info.xedges[:-1] + (info.xedges[1:] - info.xedges[:-1]) / 2
    ycenters = info.yedges[:-1] + (info.yedges[1:] - info.yedges[:-1]) / 2

    return xcenters, ycenters


def find_subset_zones(info, remove_feeder, expand_by):
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
        Keys are u, shortcut, novel.

    """
    u_line = LineString(info.u_trajectory)
    shortcut_line = LineString(info.shortcut_trajectory)
    novel_line = LineString(info.novel_trajectory)
    u_subset_line = LineString(info.u_segment)

    feeder1 = Point(info.path_pts['feeder1'][0], info.path_pts['feeder1'][1]).buffer(expand_by*1.3)
    feeder2 = Point(info.path_pts['feeder2'][0], info.path_pts['feeder2'][1]).buffer(expand_by*1.3)

    u_zone = expand_line(Point(info.u_trajectory[0]),
                         Point(info.u_trajectory[-1]),
                         u_line, expand_by)
    shortcut_zone = expand_line(Point(info.shortcut_trajectory[0]),
                                Point(info.shortcut_trajectory[-1]),
                                shortcut_line, expand_by)
    novel_zone = expand_line(Point(info.novel_trajectory[0]),
                             Point(info.novel_trajectory[-1]),
                             novel_line, expand_by)
    u_subset_zone = expand_line(Point(info.u_segment[0]),
                                Point(info.u_segment[-1]),
                                u_subset_line, expand_by)

    zone = dict()
    zone['u'] = u_subset_zone
    zone['shortcut'] = shortcut_zone.difference(u_zone)
    zone['shortcut'] = zone['shortcut'].difference(novel_zone)
    zone['novel'] = novel_zone.difference(u_zone)

    if remove_feeder:
        for feeder in [feeder1, feeder2]:
            zone['u'] = zone['u'].difference(feeder)
            zone['shortcut'] = zone['shortcut'].difference(feeder)
            zone['novel'] = zone['novel'].difference(feeder)

    return zone


def get_subset_zones(info, position):

    binned_maze_shape = (len(info.yedges)-1, len(info.xedges)-1)

    zones = find_subset_zones(info, remove_feeder=True, expand_by=15)

    xcenters, ycenters = get_bin_centers(info)

    u_zone = np.zeros(binned_maze_shape).astype(bool)
    shortcut_zone = np.zeros(binned_maze_shape).astype(bool)
    novel_zone = np.zeros(binned_maze_shape).astype(bool)

    for i, x in enumerate(xcenters):
        for j, y in enumerate(ycenters):
            if zones["u"].contains(Point(x,y)):
                u_zone[j][i] = True
            elif zones["shortcut"].contains(Point(x,y)):
                shortcut_zone[j][i] = True
            elif zones["novel"].contains(Point(x,y)):
                novel_zone[j][i] = True

    sliced_position = position.time_slice(info.task_times["phase3"].start, info.task_times["phase3"].stop)
    occupancy = nept.get_occupancy(sliced_position, info.yedges, info.xedges)

    phase1_position = position.time_slice(info.task_times["phase1"].start, info.task_times["phase1"].stop)
    phase1_occupancy = nept.get_occupancy(phase1_position, info.yedges, info.xedges)
    phase2_position = position.time_slice(info.task_times["phase2"].start, info.task_times["phase2"].stop)
    phase2_occupancy = nept.get_occupancy(phase2_position, info.yedges, info.xedges)
    u_pos = np.zeros(binned_maze_shape).astype(bool)
    u_pos[occupancy > 0.] = True
    u_pos[phase1_occupancy > 0.] = True
    u_pos[phase2_occupancy > 0.] = True
    u_area = np.zeros(binned_maze_shape).astype(bool)
    u_area[u_pos & u_zone] = True

    shortcut_pos = np.zeros(binned_maze_shape).astype(bool)
    shortcut_pos[(occupancy > 0.) & (~u_area)] = True
    shortcut_area = np.zeros(binned_maze_shape).astype(bool)
    shortcut_area[shortcut_pos & shortcut_zone] = True

    novel_pos = np.zeros(binned_maze_shape).astype(bool)
    novel_pos[(occupancy > 0.) & (~u_area)] = True
    novel_area = np.zeros(binned_maze_shape).astype(bool)
    novel_area[novel_pos & novel_zone] = True

    return u_area, shortcut_area, novel_area


def get_xy_idx(info, position):
    xcenters, ycenters = get_bin_centers(info)

    x_idx = []
    y_idx = []
    for x, y in zip(position.x, position.y):
        x_idx.append(nept.find_nearest_idx(xcenters, x))
        y_idx.append(nept.find_nearest_idx(ycenters, y))
    return x_idx, y_idx


def trials_by_trajectory(info, sliced_position, zone, min_epoch=1., min_distance=20.,
                         merge_gap=1.5, min_coverage=True):
    if min_coverage:
        min_coverage = np.sum(zone) / 4
    else:
        min_coverage = 1

    x_idxs, y_idxs = get_xy_idx(info, sliced_position)

    in_zone = zone[y_idxs, x_idxs]

    jumps = np.diff(in_zone.astype(int))
    jumps = np.insert(jumps, 0, 0)

    starts = sliced_position.time[jumps == 1]
    np.insert(starts, 0, sliced_position.time[0])
    stops = sliced_position.time[jumps == -1]
    np.insert(stops, 0, sliced_position.time[-1])

    if len(starts) < len(stops):
        stops = stops[1:]
    elif len(starts) > len(stops):
        starts = starts[:-1]

    zone_epochs = nept.Epoch([starts, stops]).merge(gap=merge_gap)

    dur_idx = zone_epochs.durations >= min_epoch

    start_idxs = [nept.find_nearest_idx(sliced_position.time, start) for start in zone_epochs.starts]
    stop_idxs = [nept.find_nearest_idx(sliced_position.time, stop) for stop in zone_epochs.stops]

    dist_idx = np.zeros(zone_epochs.n_epochs).astype(bool)
    for i, (start_idx, stop_idx) in enumerate(zip(start_idxs, stop_idxs)):
        dist_idx[i] = sliced_position[start_idx].distance(sliced_position[stop_idx])[0] > min_distance

    trial_epochs = nept.Epoch([zone_epochs.starts[dur_idx & dist_idx], zone_epochs.stops[dur_idx & dist_idx]])

    trial_starts = []
    trial_stops = []
    for start, stop in zip(trial_epochs.starts, trial_epochs.stops):
        pp = sliced_position.time_slice(start, stop)
        x_idx, y_idx = get_xy_idx(info, pp)

        if (len(np.unique([(x, y) for (x, y) in zip(x_idx, y_idx)])) > min_coverage):
            trial_starts.append(start)
            trial_stops.append(stop)

    return nept.Epoch([trial_starts, trial_stops])


def find_matched_trials(fewest_epochs, trials_to_match):
    starts = []
    stops = []
    centers = trials_to_match.centers
    for trial_center in fewest_epochs.centers:
        idx = np.nanargmin(np.abs(centers - trial_center))
        starts.append(trials_to_match[idx].start)
        stops.append(trials_to_match[idx].stop)
        centers[idx] = np.nan
    return nept.Epoch([starts, stops])


def get_matched_trials(info, sliced_position):
    u_zone, shortcut_zone, novel_zone = get_subset_zones(info, sliced_position)

    u_epochs = trials_by_trajectory(info, sliced_position, u_zone)
    shortcut_epochs = trials_by_trajectory(info, sliced_position, shortcut_zone)
    novel_epochs = trials_by_trajectory(info, sliced_position, novel_zone, min_distance=0.)
    trial_epochs = [u_epochs, shortcut_epochs, novel_epochs]

    fewest_trials = trial_epochs[np.argmin([epoch.n_epochs for epoch in trial_epochs])]

    matched_trials = nept.Epoch([], [])
    for trial_epoch in trial_epochs:
        matched_trials = matched_trials.join(find_matched_trials(fewest_trials, trial_epoch))

    return matched_trials
