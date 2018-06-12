import os
import numpy as np
import scipy
import pickle
from shapely.geometry import Point

import nept

from loading_data import get_data
from utils_maze import find_zones

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


def get_decoded(info, dt, gaussian_std, min_neurons, min_spikes, min_swr, neurons, normalized, run_time,
                speed_limit, shuffle_id, window, decoding_times, min_proportion_decoded,
                decode_sequences, sequence_len=3, sequence_speed=5., min_epochs=3, random_shuffle=False):
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
    speed_limit: float
    sequence_speed: float
    shuffle_id: boolean
    window: float
    min_proportion_decoded: float
    decoding_times: nept.Epoch
    decode_sequences: bool
    sequence_len: int
    sequence_speed: float
    random_shuffle: bool

    Returns
    -------
    decoded: nept.Position
    decoded_epochs: nept.Epoch
    errors: np.array

    """
    if decoding_times.n_epochs != 1:
        raise AssertionError("decoding_times must only contain one epoch (start, stop)")

    events, position, all_spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = nept.get_xyedges(position)

    sliced_spikes = neurons.time_slice(decoding_times.start, decoding_times.stop)
    position = position.time_slice(decoding_times.start, decoding_times.stop)

    sliced_spikes = sliced_spikes.spikes

    if shuffle_id:
        tuning_curves = np.random.permutation(neurons.tuning_curves)
    else:
        tuning_curves = neurons.tuning_curves

    if run_time:
        # limit position to only times when the subject is moving faster than a certain threshold
        run_epoch = nept.run_threshold(position, thresh=speed_limit)
        position = position[run_epoch]

        epochs_interest = nept.Epoch(np.array([position.time[0], position.time[-1]]))
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

    if random_shuffle:
        random_x = [np.random.choice(decoded.x) for val in decoded.x]
        random_y = [np.random.choice(decoded.y) for val in decoded.y]

        decoded = nept.Position(np.array([random_x, random_y]).T, decoded.time)

    if decode_sequences:
        print('decoded n_samples before sequence:', decoded.n_samples)
        sequences = nept.remove_teleports(decoded, speed_thresh=sequence_speed, min_length=sequence_len)
        decoded_epochs = epochs_interest.intersect(sequences)
        decoded_epochs = decoded_epochs.expand(0.002)

        if decoded_epochs.n_epochs < min_epochs:
            decoded = nept.Position(np.array([]), np.array([]))
        else:
            decoded = decoded[decoded_epochs]

        print('decoded n_samples after sequence:', decoded.n_samples)
    else:
        decoded_epochs = epochs_interest

    f_xy = scipy.interpolate.interp1d(position.time, position.data.T, kind="nearest")
    decoded_xy = f_xy(decoded.time)
    actual_position = nept.Position(np.hstack((decoded_xy[0][..., np.newaxis],
                                               decoded_xy[1][..., np.newaxis])),
                                    decoded.time)

    if decoded.n_samples > 0:
        errors = actual_position.distance(decoded)
    else:
        errors = np.array([])

    percent_decoded = (decoded.n_samples/counts.n_samples)*100

    if (decoded.n_samples/counts.n_samples) < min_proportion_decoded:
        print("Decoded bins make up %d%% of possible bins ..."
              "removing due to too few bins" % percent_decoded)

        decoded = nept.Position([np.array([]), np.array([])], np.array([]))
        decoded_epochs = nept.Epoch([np.array([]), np.array([])])
        errors = np.array([])
        actual_position = nept.Position([np.array([]), np.array([])], np.array([]))

    return decoded, decoded_epochs, errors, actual_position, likelihood, percent_decoded


def get_decoded_zones(info, decoded, position, experiment_time):
    """Assigns decoded position to zone and computes error

    Parameters
    ----------
    info: module
    decoded: nept.Position
    position: nept.Position
    experiment_time: str

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
                errors[trajectory] = []

    else:
        for trajectory in decoded_zones:
            errors[trajectory] = []
            actual_position[trajectory] = []

    return decoded_zones, errors, actual_position


def zone_sort(info, decoded, shuffle_id, experiment_time):
    """Evaluates decoded analysis

    Parameters
    ----------
    info: module
    decoded: dict
    shuffle_id: boolean
    experiment_time: str

    Returns
    -------
    decoded_output: dict

    """
    decoded_zones, zone_errors, actual_position = get_decoded_zones(info, decoded["decoded"], decoded["position"],
                                                                    experiment_time)

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

                args = dict(min_swr=3,
                            min_neurons=2,
                            min_spikes=1,
                            neurons=neurons,
                            info=session,
                            normalized=False,
                            sequence_speed=5.,
                            sequence_len=3,
                            min_epochs=3,
                            window=0.025,
                            dt=0.025,
                            gaussian_std=0.0075,
                            experiment_time=experiment_time,
                            speed_limit=4.)
                if experiment_time in track_times:
                    args["run_time"] = True
                else:
                    args["run_time"] = False
                if shuffled:
                    args["shuffle_id"] = True
                else:
                    args["shuffle_id"] = False

                print('decoding: %s %s; shuffled: %s' % (session.session_id, experiment_time, shuffled))

                decode = {}
                decode['decoded'], decode['decoded_epochs'], decode['errors'], decode['position'] = get_decoded(**args)
                zone_sort(session, decode, shuffled, experiment_time)
