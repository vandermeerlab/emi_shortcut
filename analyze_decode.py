import os
import numpy as np
import random
import pickle
from shapely.geometry import Point, LineString

import vdmlab as vdm

from loading_data import get_data
from utils_maze import find_zones, get_xyedges, speed_threshold

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')

def get_edges(position, binsize, lastbin=False):
    """Finds edges based on linear time

    Parameters
    ----------
    position : vdmlab.Position
    binsize : float
        This is the desired size of bin.
        Typically set around 0.020 to 0.040 seconds.
    lastbin : boolean
        Determines whether to include the last bin. This last bin may
        not have the same binsize as the other bins.

    Returns
    -------
    edges : np.array

    """
    edges = np.arange(position.time[0], position.time[-1], binsize)

    if lastbin:
        if edges[-1] != position.time[-1]:
            edges = np.hstack((edges, position.time[-1]))

    return edges


def point_in_zones(position, zones):
    """Assigns points if contained in shortcut zones

    Parameters
    ----------
    position : vdmlab.Position
    zones : dict
        With u, ushort, unovel, shortcut, shortped, novel, novelped, pedestal as keys

    Returns
    -------
    sorted_zones : dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object

    """
    u_data = []
    u_times = []
    shortcut_data = []
    shortcut_times = []
    novel_data = []
    novel_times = []
    other_data = []
    other_times = []

    for x, y, time in zip(position.x, position.y, position.time):
        point = Point([x, y])
        if zones['u'].contains(point) or zones['ushort'].contains(point) or zones['unovel'].contains(point):
            u_data.append([x, y])
            u_times.append(time)
            continue
        elif zones['shortcut'].contains(point) or zones['shortped'].contains(point):
            shortcut_data.append([x, y])
            shortcut_times.append(time)
            continue
        elif zones['novel'].contains(point) or zones['novelped'].contains(point):
            novel_data.append([x, y])
            novel_times.append(time)
            continue
        else:
            other_data.append([x, y])
            other_times.append(time)

    sorted_zones = dict()
    sorted_zones['u'] = vdm.Position(u_data, u_times)
    sorted_zones['shortcut'] = vdm.Position(shortcut_data, shortcut_times)
    sorted_zones['novel'] = vdm.Position(novel_data, novel_times)
    sorted_zones['other'] = vdm.Position(other_data, other_times)

    return sorted_zones


def compare_rates(zones, jump=0.1):
    """Compare position normalized by time spent in zone.

    Parameters
    ----------
    zones: dict
        With u, shortcut, novel, other as keys.
    jump: float
        Any duration above this amount will not be included.

    Returns
    -------
    normalized : dict
        With u, shortcut, novel as keys.

    """
    u_linger = np.diff(zones['u'].time)
    shortcut_linger = np.diff(zones['shortcut'].time)
    novel_linger = np.diff(zones['novel'].time)

    u_linger = np.sum(u_linger[u_linger < jump])
    shortcut_linger = np.sum(shortcut_linger[shortcut_linger < jump])
    novel_linger = np.sum(novel_linger[novel_linger < jump])

    normalized = dict()
    normalized['u'] = len(zones['u'].time) / u_linger
    normalized['shortcut'] = len(zones['shortcut'].time) / shortcut_linger
    normalized['novel'] = len(zones['novel'].time) / novel_linger

    return normalized


def compare_lengths(zones, lengths):
    """Compare position normalized by time spent in zone.

    Parameters
    ----------
    zones: dict
        With u, shortcut, novel, other as keys.
    lengths: dict
        With u, shortcut, novel as keys.

    Returns
    -------
    normalized : dict
        With u, shortcut, novel as keys.

    """
    normalized = dict()
    normalized['u'] = len(zones['u'].time) / lengths['u']
    normalized['shortcut'] = len(zones['shortcut'].time) / lengths['shortcut']
    normalized['novel'] = len(zones['novel'].time) / lengths['novel']

    return normalized


def analyze(info, tuning_curve, experiment_time='tracks', shuffle_id=False):
    """Finds decoded for each session.

    Parameters
    ----------
    info: module
    tuning_curves: np.array
    experiment_time: str
    shuffle_id: bool
        Defaults to False (not shuffled)

    Returns
    -------
    combined_decoded: dict of vdmlab.Position objects
        With u, shortcut, novel, other, together as keys.
    combined_errors: list of np.arrays
    total_times: list

    """
    print('decoding:', info.session_id)

    track_times = ['phase1', 'phase2', 'phase3', 'tracks']
    pedestal_times = ['pauseA', 'pauseB', 'prerecord', 'postrecord']

    events, position, spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = get_xyedges(position)

    if experiment_time in track_times:
        run_pos = speed_threshold(position, speed_limit=0.4)
    else:
        run_pos = position

    track_starts = [info.task_times[experiment_time].start]
    track_stops = [info.task_times[experiment_time].stop]

    track_pos = run_pos.time_slices(track_starts, track_stops)

    if shuffle_id:
        random.shuffle(tuning_curve)

    start = np.array([info.task_times[experiment_time].start])
    stop = np.array([info.task_times[experiment_time].stop])

    decode_spikes = [spiketrain.time_slices(start, stop) for spiketrain in spikes]

    if experiment_time in track_times:
        epochs_interest = vdm.Epoch(np.hstack([start, stop]))
    elif experiment_time in pedestal_times:
        sliced_lfp = lfp.time_slice(start, stop)

        z_thresh = 3.0
        power_thresh = 5.0
        merge_thresh = 0.02
        min_length = 0.01
        swrs = vdm.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                      power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

        epochs_interest = vdm.find_multi_in_epochs(decode_spikes, swrs, min_involved=3)
        if epochs_interest.n_epochs == 0:
            epochs_interest = vdm.find_multi_in_epochs(decode_spikes, swrs, min_involved=1)
    else:
        raise ValueError("unrecognized experimental phase. Must be in ['prerecord', 'phase1', 'pauseA', 'phase2', "
                         "'pauseB', phase3', 'postrecord'].")

    counts_binsize = 0.025
    time_edges = get_edges(track_pos, counts_binsize, lastbin=True)
    counts = vdm.get_counts(decode_spikes, time_edges, gaussian_std=0.005)

    tc_shape = tuning_curve.shape
    decoding_tc = tuning_curve.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

    likelihood = vdm.bayesian_prob(counts, decoding_tc, counts_binsize)

    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.
    xy_centers = vdm.cartesian(xcenters, ycenters)

    time_centers = (time_edges[1:] + time_edges[:-1]) / 2.

    decoded = vdm.decode_location(likelihood, xy_centers, time_centers)
    nan_idx = np.logical_and(np.isnan(decoded.x), np.isnan(decoded.y))
    decoded = decoded[~nan_idx]

    if not decoded.isempty:
        sequences = vdm.remove_teleports(decoded, speed_thresh=40, min_length=3)
        decoded_epochs = sequences.intersect(epochs_interest)
        decoded = vdm.epoch_position(decoded, decoded_epochs)
    else:
        raise ValueError("decoded cannot be empty.")

    zones = find_zones(info, expand_by=8)
    decoded_zones = point_in_zones(decoded, zones)

    keys = ['u', 'shortcut', 'novel']
    errors = dict()
    actual_position = dict()
    if experiment_time in ['phase1', 'phase2', 'phase3', 'tracks']:
        for trajectory in keys:
            actual_x = np.interp(decoded_zones[trajectory].time, track_pos.time, track_pos.x)
            actual_y = np.interp(decoded_zones[trajectory].time, track_pos.time, track_pos.y)
            actual_position[trajectory] = vdm.Position(np.hstack((actual_x[..., np.newaxis],
                                                                  actual_y[..., np.newaxis])),
                                                       decoded_zones[trajectory].time)
            errors[trajectory] = actual_position[trajectory].distance(decoded_zones[trajectory])
    else:
        for trajectory in decoded_zones:
            errors[trajectory] = []
            actual_position[trajectory] = []

    output = dict()
    output['zones'] = decoded_zones
    output['errors'] = errors
    output['times'] = len(time_centers)
    output['actual'] = actual_position
    output['decoded'] = decoded

    if experiment_time == 'tracks':
        if shuffle_id:
            filename = info.session_id + '_decode-tracks-shuffled.pkl'
        else:
            filename = info.session_id + '_decode-tracks.pkl'
    else:
        if shuffle_id:
            filename = info.session_id + '_decode-pauses-shuffled.pkl'
        else:
            filename = info.session_id + '_decode-' + experiment_time + '.pkl'

    pickled_path = os.path.join(pickle_filepath, filename)

    with open(pickled_path, 'wb') as fileobj:
        pickle.dump(output, fileobj)

    return output


def combine_decode(infos, filename, experiment_time, shuffle_id, tuning_curves=None):
    total_times = []
    combined_errors = []
    combined_lengths = dict(u=[], shortcut=[], novel=[], other=[], together=[])
    combined_decoded = dict(u=[], shortcut=[], novel=[], other=[], together=[])

    for i, info in enumerate(infos):
        decode_filename = info.session_id + filename
        pickled_decoded = os.path.join(pickle_filepath, decode_filename)

        if os.path.isfile(pickled_decoded):
            with open(pickled_decoded, 'rb') as fileobj:
                decoded = pickle.load(fileobj)
        else:
            if tuning_curves is None:
                raise ValueError("tuning curves required when generating decoded")
            decoded = analyze(info, tuning_curves[i], experiment_time=experiment_time, shuffle_id=shuffle_id)

        total_times.append(decoded['times'])

        combined_lengths['u'].append(LineString(info.u_trajectory).length)
        combined_lengths['shortcut'].append(LineString(info.shortcut_trajectory).length)
        combined_lengths['novel'].append(LineString(info.novel_trajectory).length)

        combined_decoded['u'].append(decoded['zones']['u'])
        combined_decoded['shortcut'].append(decoded['zones']['shortcut'])
        combined_decoded['novel'].append(decoded['zones']['novel'])
        combined_decoded['other'].append(decoded['zones']['other'])
        combined_decoded['together'].append(len(decoded['zones']['u'].time) +
                                            len(decoded['zones']['shortcut'].time) +
                                            len(decoded['zones']['novel'].time) +
                                            len(decoded['zones']['other'].time))

        keys = ['u', 'shortcut', 'novel']
        combined_errors = dict(u=[], shortcut=[], novel=[], together=[])
        for trajectory in keys:
            combined_errors[trajectory].extend(decoded['errors'][trajectory])
            combined_errors['together'].extend(decoded['errors'][trajectory])

    output = dict()
    output['combined_decoded'] = combined_decoded
    output['combined_errors'] = combined_errors
    output['total_times'] = total_times
    output['combined_lengths'] = combined_lengths

    return output

outputs_tracks = []

if __name__ == "__main__":
    from run import spike_sorted_infos

    infos = spike_sorted_infos

    if 1:
        for info in infos:
            tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
            pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
            with open(pickled_tuning_curve, 'rb') as fileobj:
                tuning_curve = pickle.load(fileobj)
            experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']
            # experiment_times = ['pauseA', 'pauseB']
            for experiment_time in experiment_times:
                analyze(info, tuning_curve, experiment_time)

    if 0:
        tuning_curves = []
        for info in infos:
            tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
            pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
            with open(pickled_tuning_curve, 'rb') as fileobj:
                tuning_curves.append(pickle.load(fileobj))
        decoded_tracks = combine_decode(infos, '_decode-tracks.pkl', experiment_time='tracks',
                                        shuffle_id=False, tuning_curves=tuning_curves)
        decoded_tracks_shuffled = combine_decode(infos, '_decode-tracks_shuffled.pkl', experiment_time='tracks',
                                                 shuffle_id=True, tuning_curves=tuning_curves)

    if 0:
        for info in infos:
            tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
            pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
            with open(pickled_tuning_curve, 'rb') as fileobj:
                tuning_curve = pickle.load(fileobj)
            experiment_time = 'pauseA'
            decoded_pausea = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                            shuffle_id=False, tuning_curves=tuning_curve)
            experiment_time = 'pauseB'
            decoded_pauseb = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                            shuffle_id=False, tuning_curves=tuning_curve)
