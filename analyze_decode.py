import os
import numpy as np
import pickle
from shapely.geometry import Point, LineString

import nept

from loading_data import get_data
from utils_maze import find_zones, speed_threshold

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')


def point_in_zones(position, zones):
    """Assigns points if contained in shortcut zones

    Parameters
    ----------
    position : nept.Position
    zones : dict
        With u, shortcut, novel, pedestal as keys

    Returns
    -------
    sorted_zones : dict
        With u, shortcut, novel, other as keys, each a nept.Position object

    """
    u_data = []
    u_times = []
    shortcut_data = []
    shortcut_times = []
    novel_data = []
    novel_times = []
    other_data = []
    other_times = []

    if not position.isempty:
        for x, y, time in zip(position.x, position.y, position.time):
            point = Point([x, y])
            if zones['u'].contains(point):
                u_data.append([x, y])
                u_times.append(time)
                continue
            elif zones['shortcut'].contains(point):
                shortcut_data.append([x, y])
                shortcut_times.append(time)
                continue
            elif zones['novel'].contains(point):
                novel_data.append([x, y])
                novel_times.append(time)
                continue
            else:
                other_data.append([x, y])
                other_times.append(time)

    sorted_zones = dict()
    sorted_zones['u'] = nept.Position(u_data, u_times)
    sorted_zones['shortcut'] = nept.Position(shortcut_data, shortcut_times)
    sorted_zones['novel'] = nept.Position(novel_data, novel_times)
    sorted_zones['other'] = nept.Position(other_data, other_times)

    return sorted_zones


def get_decoded(info, neurons, experiment_time, speed_limit, shuffle_id, min_swr=3):
    """Finds decoded for each session.

    Parameters
    ----------
    info: module
    neurons: nept.Neurons
    experiment_time: str
    shuffle_id: bool

    Returns
    -------
    decoded: dict of nept.Position objects
        With u, shortcut, novel, other as keys.

    """
    print('decoding:', info.session_id, experiment_time)

    track_times = ['phase1', 'phase2', 'phase3', 'tracks']
    pedestal_times = ['pauseA', 'pauseB', 'prerecord', 'postrecord']

    events, position, all_spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = nept.get_xyedges(position)

    exp_start = info.task_times[experiment_time].start
    exp_stop = info.task_times[experiment_time].stop

    sliced_spikes = neurons.time_slice(exp_start, exp_stop)

    if experiment_time in track_times:
        run_position = speed_threshold(position, speed_limit=speed_limit)
    else:
        run_position = position

    exp_position = run_position.time_slice(exp_start, exp_stop)

    if shuffle_id:
        tuning_curves = np.random.permutation(neurons.tuning_curves)
    else:
        tuning_curves = neurons.tuning_curves

    if experiment_time in track_times:
        epochs_interest = nept.Epoch(np.hstack([exp_start, exp_stop]))
    elif experiment_time in pedestal_times:
        sliced_lfp = lfp.time_slice(exp_start, exp_stop)

        z_thresh = 3.0
        power_thresh = 5.0
        merge_thresh = 0.02
        min_length = 0.05
        swrs = nept.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                       power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

        # print('sharp-wave ripples, total:', swrs.n_epochs)

        min_involved = 4
        epochs_interest = nept.find_multi_in_epochs(sliced_spikes, swrs, min_involved=min_involved)

        # print('sharp-wave ripples, min', min_involved, 'neurons :', epochs_interest.n_epochs)

        if epochs_interest.n_epochs < min_swr:
            epochs_interest = nept.Epoch(np.array([[], []]))

        # print('sharp-wave ripples, used :', epochs_interest.n_epochs)
        # print('sharp-wave ripples, mean durations: ', np.mean(epochs_interest.durations))
    else:
        raise ValueError("unrecognized experimental phase. Must be in ['prerecord', 'phase1', 'pauseA', 'phase2', "
                         "'pauseB', phase3', 'postrecord'].")

    window_size = 0.020
    window_advance = 0.005
    time_edges = nept.get_edges(exp_position, window_advance, lastbin=True)
    counts = nept.bin_spikes(sliced_spikes, exp_position, window_size, window_advance,
                             gaussian_std=0.006, normalized=False)

    tc_shape = tuning_curves.shape
    decoding_tc = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

    likelihood = nept.bayesian_prob(counts, decoding_tc, window_advance)

    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.
    xy_centers = nept.cartesian(xcenters, ycenters)

    decoded = nept.decode_location(likelihood, xy_centers, time_edges)
    nan_idx = np.logical_and(np.isnan(decoded.x), np.isnan(decoded.y))
    decoded = decoded[~nan_idx]

    output = dict()
    output['decoded'] = decoded
    output['epochs_interest'] = epochs_interest
    output['time_edges'] = time_edges
    output['exp_position'] = exp_position

    return output


def analyze(info, neurons, experiment_time, shuffle_id, min_sequence=3, speed_limit=0.4, min_epochs=3):
    """Evaluates decoded analysis

    Parameters
    ----------
    info: module
    neurons: nept.Neurons
    experiment_time: str
    shuffle_id: bool
    min_sequence: int
    speed_limit: float
    min_epochs: int

    Returns
    -------
    decoded_output: dict

    """
    decode = get_decoded(info, neurons, experiment_time, speed_limit=speed_limit, shuffle_id=shuffle_id)
    decoded = decode['decoded']
    epochs_interest = decode['epochs_interest']
    time_edges = decode['time_edges']
    exp_position = decode['exp_position']

    sequences = nept.remove_teleports(decoded, speed_thresh=10, min_length=min_sequence)
    decoded_epochs = epochs_interest.intersect(sequences)
    decoded_epochs = decoded_epochs.expand(0.05)

    print('number of positions that are sequences and overlap epochs: ', decoded_epochs.n_epochs)

    if decoded_epochs.n_epochs < min_epochs:
        decoded = nept.Position(np.array([[], []]), np.array([]))
    else:
        decoded = decoded[decoded_epochs]

    zones = find_zones(info, remove_feeder=True, expand_by=8)
    decoded_zones = point_in_zones(decoded, zones)

    keys = ['u', 'shortcut', 'novel']
    errors = dict()
    actual_position = dict()
    if experiment_time in ['phase1', 'phase2', 'phase3', 'tracks']:
        for trajectory in keys:
            actual_x = np.interp(decoded_zones[trajectory].time, exp_position.time, exp_position.x)
            actual_y = np.interp(decoded_zones[trajectory].time, exp_position.time, exp_position.y)
            actual_position[trajectory] = nept.Position(np.hstack((actual_x[..., np.newaxis],
                                                                  actual_y[..., np.newaxis])),
                                                        decoded_zones[trajectory].time)

            if actual_position[trajectory].n_samples > 0:
                errors[trajectory] = actual_position[trajectory].distance(decoded_zones[trajectory])
    else:
        for trajectory in decoded_zones:
            errors[trajectory] = []
            actual_position[trajectory] = []

    output = dict()
    output['zones'] = decoded_zones
    output['errors'] = errors
    output['times'] = len(time_edges)
    output['actual'] = actual_position
    output['decoded'] = decoded
    output['epochs'] = decoded_epochs

    if shuffle_id:
        filename = info.session_id + '_decode-shuffled-' + experiment_time + '.pkl'
    else:
        filename = info.session_id + '_decode-' + experiment_time + '.pkl'

    pickled_path = os.path.join(pickle_filepath, filename)

    with open(pickled_path, 'wb') as fileobj:
        pickle.dump(output, fileobj)

    return output


if __name__ == "__main__":
    from run import spike_sorted_infos, info
    # infos = spike_sorted_infos
    infos = [info.r066d3]

    if 1:
        for info in infos:
            neurons_filename = info.session_id + '_neurons.pkl'
            pickled_neurons = os.path.join(pickle_filepath, neurons_filename)
            with open(pickled_neurons, 'rb') as fileobj:
                neurons = pickle.load(fileobj)
            experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']
            # experiment_times = ['pauseA', 'pauseB']
            for experiment_time in experiment_times:
                analyze(info, neurons, experiment_time, shuffle_id=False)

    # shuffled_id
    if 1:
        for info in infos:
            neurons_filename = info.session_id + '_neurons.pkl'
            pickled_neurons = os.path.join(pickle_filepath, neurons_filename)
            with open(pickled_neurons, 'rb') as fileobj:
                neurons = pickle.load(fileobj)
            experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']
            for experiment_time in experiment_times:
                analyze(info, neurons, experiment_time, shuffle_id=True)
