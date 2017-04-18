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


def get_decoded(info, dt, gaussian_std, min_epochs, min_neurons, min_spikes, min_swr, neurons, normalized, run_time,
                sequence_len, sequence_speed, shuffle_id, speed_limit, t_start, t_stop, window):
    """Finds decoded for each session.

    Parameters
    ----------
    info: module
    dt: float
    gaussian_std: float
    min_epochs: int
    min_neurons: int
    min_spikes: int
    min_swr: int
    neurons: nept.Neurons
    normalized: boolean
    run_time: boolean
    sequence_len: int
    sequence_speed: float
    shuffle_id: boolean
    speed_limit: float
    t_start: float
    t_stop: float
    window: float

    Returns
    -------
    decoded: nept.Position
    decoded_epochs: nept.Epoch
    errors: np.array

    """
    events, position, all_spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = nept.get_xyedges(position)

    sliced_spikes = neurons.time_slice(t_start, t_stop)
    sliced_spikes = sliced_spikes.spikes

    position = position.time_slice(t_start, t_stop)

    if shuffle_id:
        tuning_curves = np.random.permutation(neurons.tuning_curves)
    else:
        tuning_curves = neurons.tuning_curves

    if run_time:
        epochs_interest = speed_threshold(position, speed_limit=speed_limit)
    else:
        sliced_lfp = lfp.time_slice(t_start, t_stop)

        z_thresh = 3.0
        power_thresh = 5.0
        merge_thresh = 0.02
        min_length = 0.05
        swrs = nept.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                       power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

        min_involved = 4
        multi_swr = nept.find_multi_in_epochs(sliced_spikes, swrs, min_involved=min_involved)

        if multi_swr.n_epochs < min_swr:
            epochs_interest = nept.Epoch(np.array([[], []]))
        else:
            epochs_interest = multi_swr

        # print('sharp-wave ripples, total:', swrs.n_epochs)
        # print('sharp-wave ripples, min', min_involved, 'neurons :', multi_swr.n_epochs)
        # print('sharp-wave ripples, used :', epochs_interest.n_epochs)
        # print('sharp-wave ripples, mean durations: ', np.mean(epochs_interest.durations))

    counts = nept.bin_spikes(sliced_spikes, position.time, dt=dt, window=window,
                             gaussian_std=gaussian_std, normalized=normalized)

    tc_shape = tuning_curves.shape
    decoding_tc = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

    likelihood = nept.bayesian_prob(counts, decoding_tc, window, min_neurons=min_neurons, min_spikes=min_spikes)

    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.
    xy_centers = nept.cartesian(xcenters, ycenters)

    decoded = nept.decode_location(likelihood, xy_centers, counts.time)
    nan_idx = np.logical_and(np.isnan(decoded.x), np.isnan(decoded.y))
    decoded = decoded[~nan_idx]

    sequences = nept.remove_teleports(decoded, speed_thresh=sequence_speed, min_length=sequence_len)
    decoded_epochs = epochs_interest.intersect(sequences)
    decoded_epochs = decoded_epochs.expand(0.005)

    if decoded_epochs.n_epochs < min_epochs:
        decoded = nept.Position(np.array([]), np.array([]))
    else:
        decoded = decoded[decoded_epochs]

    actual_x = np.interp(decoded.time, position.time, position.x)
    actual_y = np.interp(decoded.time, position.time, position.y)
    actual_position = nept.Position(np.hstack((actual_x[..., np.newaxis],
                                               actual_y[..., np.newaxis])), decoded.time)
    if decoded.n_samples > 0:
        errors = actual_position.distance(decoded)
    else:
        errors = np.nan

    return decoded, decoded_epochs, errors, actual_position


def get_decoded_zones(info, decoded, position):
    """Assigns decoded position to zone and computes error

    Parameters
    ----------
    info: module
    decoded: nept.Position
    position: nept.Position

    Returns
    -------
    decoded_zones: dict
        With u, shortcut, novel as keys.
    errors: dict
        With u, shortcut, novel as keys.
    actual_position: dict
        With u, shortcut, novel as keys.

    """
    zones = find_zones(info, remove_feeder=True, expand_by=8)
    decoded_zones = point_in_zones(decoded, zones)

    keys = ['u', 'shortcut', 'novel']

    errors = dict()
    actual_position = dict()
    if experiment_time in ['phase1', 'phase2', 'phase3', 'tracks']:
        for trajectory in keys:
            actual_x = np.interp(decoded_zones[trajectory].time, position.time, position.x)
            actual_y = np.interp(decoded_zones[trajectory].time, position.time, position.y)
            actual_position[trajectory] = nept.Position(np.hstack((actual_x[..., np.newaxis],
                                                                   actual_y[..., np.newaxis])),
                                                        decoded_zones[trajectory].time)
            if actual_position[trajectory].n_samples > 0:
                errors[trajectory] = actual_position[trajectory].distance(decoded_zones[trajectory])
    else:
        for trajectory in decoded_zones:
            errors[trajectory] = []
            actual_position[trajectory] = []

    return decoded_zones, errors, actual_position


def zone_sort(info, decoded, shuffle_id):
    """Evaluates decoded analysis

    Parameters
    ----------
    info: module
    decoded: dict
    shuffle_id: boolean

    Returns
    -------
    decoded_output: dict

    """
    decoded_zones, zone_errors, actual_position = get_decoded_zones(info, decoded["decoded"], decoded["position"])

    output = dict()
    output['zones'] = decoded_zones
    output['errors'] = decoded["errors"]
    output['zone_errors'] = zone_errors
    output['times'] = decoded["decoded"].n_samples
    output['actual'] = actual_position
    output['decoded'] = decoded["decoded"]
    output['epochs'] = decoded["decoded_epochs"]

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
    infos = [info.r063d2]

    if 1:
        track_times = ['phase1', 'phase2', 'phase3', 'tracks']
        experiment_time = "phase3"

        for session in infos:
            neurons_filename = session.session_id + '_neurons.pkl'
            pickled_neurons = os.path.join(pickle_filepath, neurons_filename)
            with open(pickled_neurons, 'rb') as fileobj:
                neurons = pickle.load(fileobj)

            for shuffled in [True, False]:
                t_start = session.task_times[experiment_time].start
                t_stop = session.task_times[experiment_time].stop

                args = dict(speed_limit=0.4,
                            min_swr=3,
                            min_neurons=2,
                            min_spikes=1,
                            t_start=t_start,
                            t_stop=t_stop,
                            neurons=neurons,
                            info=session,
                            normalized=False,
                            sequence_speed=5.,
                            sequence_len=3,
                            min_epochs=3,
                            window=0.0125,
                            dt=0.0125,
                            gaussian_std=0.0075)
                if experiment_time in track_times:
                    args["run_time"] = True
                else:
                    args["run_time"] = False
                if shuffled:
                    args["shuffle_id"] = True
                else:
                    args["shuffle_id"] = False

                print('decoding:', session.session_id, experiment_time, 'shuffled:', shuffled)

                decode = {}
                decode['decoded'], decode['decoded_epochs'], decode['errors'], decode['position'] = get_decoded(**args)
                zone_sort(session, decode, shuffled)
