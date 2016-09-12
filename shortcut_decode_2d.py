import os
import numpy as np
import random
import matplotlib.pyplot as plt
import pickle
from scipy.interpolate import InterpolatedUnivariateSpline

import vdmlab as vdm

from load_data import get_pos, get_spikes
from maze_functions import find_zones
from decode_functions import get_edges, point_in_zones, compare_rates
from plotting_functions import plot_compare_decoded_track

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
import info.R063d4_info as r063d4
import info.R063d5_info as r063d5
import info.R063d6_info as r063d6
import info.R066d1_info as r066d1
import info.R066d2_info as r066d2
import info.R066d3_info as r066d3
import info.R066d4_info as r066d4
import info.R066d5_info as r066d5
import info.R067d1_info as r067d1
import info.R067d2_info as r067d2
import info.R067d3_info as r067d3
import info.R067d4_info as r067d4
import info.R067d5_info as r067d5
import info.R068d1_info as r068d1
import info.R068d2_info as r068d2
import info.R068d3_info as r068d3
import info.R068d4_info as r068d4
import info.R068d5_info as r068d5

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')

infos = [r063d2, r063d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6,
#          r066d1, r066d2, r066d3, r066d4, r066d5,
#          r067d1, r067d2, r067d3, r067d4, r067d5,
#          r068d1, r068d2, r068d3, r068d4, r068d5]

shuffle_id = False
pauseB = False

combined_errors = []
combined_actual = dict(u=[], shortcut=[], novel=[], other=[], together=[])
combined_decoded = dict(u=[], shortcut=[], novel=[], other=[], together=[])
combined_track_relative = dict(u=[], shortcut=[], novel=[])

for info in infos:
    print(info.session_id)
    position = get_pos(info.pos_mat, info.pxl_to_cm)
    spikes = get_spikes(info.spike_mat)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= 0.1
    run_pos = position[run_idx]

    # track_starts = [info.task_times['phase1'].start, info.task_times['phase2'].start, info.task_times['phase3'].start]
    # track_stops = [info.task_times['phase1'].stop, info.task_times['phase2'].stop, info.task_times['phase3'].stop]

    track_start = info.task_times['phase3'].start
    track_stop = info.task_times['phase3'].stop

    track_pos = run_pos.time_slice(track_start, track_stop)

    track_spikes = [spiketrain.time_slice(track_start, track_stop) for spiketrain in spikes]

    binsize = 3
    xedges = np.arange(track_pos.x.min(), track_pos.x.max() + binsize, binsize)
    yedges = np.arange(track_pos.y.min(), track_pos.y.max() + binsize, binsize)

    tuning_curves = vdm.tuning_curve_2d(track_pos, track_spikes, xedges, yedges, gaussian_sigma=0.1)

    if shuffle_id:
        random.shuffle(tuning_curves)

    if pauseB:
        decode_spikes = [spiketrain.time_slice(info.task_times['pauseB'].start, info.task_times['pauseB'].stop)
                         for spiketrain in spikes]
    else:
        decode_spikes = track_spikes

    counts_binsize = 0.025
    time_edges = get_edges(run_pos, counts_binsize, lastbin=True)
    counts = vdm.get_counts(decode_spikes, time_edges, gaussian_std=0.025)

    decoding_tc = []
    for tuning_curve in tuning_curves:
        decoding_tc.append(np.ravel(tuning_curve))
    decoding_tc = np.array(decoding_tc)

    likelihood = vdm.bayesian_prob(counts, decoding_tc, counts_binsize)

    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.
    xy_centers = vdm.cartesian(xcenters, ycenters)

    time_centers = (time_edges[1:] + time_edges[:-1]) / 2.

    decoded = vdm.decode_location(likelihood, xy_centers, time_centers)
    nan_idx = np.logical_and(np.isnan(decoded.x), np.isnan(decoded.y))
    decoded = decoded[~nan_idx]

    if not decoded.isempty:
        decoded = vdm.remove_teleports(decoded, speed_thresh=10, min_length=3)

    actual_x = np.interp(decoded.time, track_pos.time, track_pos.x)
    actual_y = np.interp(decoded.time, track_pos.time, track_pos.y)

    actual_position = vdm.Position(np.hstack((actual_x[..., np.newaxis], actual_y[..., np.newaxis])), decoded.time)

    errors = actual_position.distance(decoded)

    zones = find_zones(info, expand_by=7)
    actual_zones = point_in_zones(actual_position, zones)
    decoded_zones = point_in_zones(decoded, zones)


    combined_errors.append(np.mean(errors))

    combined_actual['u'].append(actual_zones['u'])
    combined_actual['shortcut'].append(actual_zones['shortcut'])
    combined_actual['novel'].append(actual_zones['novel'])
    combined_actual['other'].append(actual_zones['other'])
    combined_actual['together'].append(len(actual_zones['u'].time) + len(actual_zones['shortcut'].time) +
                                       len(actual_zones['novel'].time) + len(actual_zones['other'].time))

    combined_decoded['u'].append(decoded_zones['u'])
    combined_decoded['shortcut'].append(decoded_zones['shortcut'])
    combined_decoded['novel'].append(decoded_zones['novel'])
    combined_decoded['other'].append(decoded_zones['other'])
    combined_decoded['together'].append(len(decoded_zones['u'].time) + len(decoded_zones['shortcut'].time) +
                                        len(decoded_zones['novel'].time) + len(decoded_zones['other'].time))

    length_tracks = info.track_length['u'] + info.track_length['shortcut'] + info.track_length['novel']
    combined_track_relative['u'].append(info.track_length['u']/length_tracks)
    combined_track_relative['shortcut'].append(info.track_length['u']/length_tracks)
    combined_track_relative['novel'].append(info.track_length['u']/length_tracks)


def compare_decoded_actual(combined_actual, combined_decoded, combined_tracks, shuffle_id, pauseB, output_filepath):
    keys = ['u', 'shortcut', 'novel']

    actual = dict(u=[], shortcut=[], novel=[])
    decode = dict(u=[], shortcut=[], novel=[])

    n_sessions = len(combined_actual['together'])

    length_tracks = info.track_length['u'] + info.track_length['shortcut'] + info.track_length['novel']

    for key in keys:
        if len(combined_actual['together']) != len(combined_decoded['together']):
            raise ValueError("must have same number of decoded and actual samples")

        for val in range(n_sessions):
            if len(combined_actual[key][val].time) > 0:
                actual[key].append(len(combined_actual[key][val].time)/combined_actual['together'][val] +
                                   combined_tracks[val])
            else:
                actual[key].append(len(combined_actual[key][val].time)/combined_actual['together'][val])

            if len(combined_decoded[key][val].time) > 0:
                decode[key].append(len(combined_decoded[key][val].time)/combined_decoded['together'][val] +
                                   combined_tracks[val])
            else:
                decode[key].append(len(combined_decoded[key][val].time)/combined_decoded['together'][val])

    if shuffle_id and not pauseB:
        filename = 'combined-phase3-id_shuffle_decoded.png'
    elif shuffle_id and pauseB:
        filename = 'combined-pauseB-id_shuffle_decoded.png'
    elif pauseB and not shuffle_id:
        filename = 'combined-pauseB-id_decoded.png'
    else:
        filename = 'combined-phase3_decoded.png'
    savepath = os.path.join(output_filepath, filename)

    if pauseB:
        plot_compare_decoded_track(decode, max_y=1.0, savepath=savepath)
    else:
        plot_compare_decoded_track(decode, actual, distance=str(round(np.mean(combined_errors), 2)),
                                   max_y=1.0, savepath=savepath)

    print('Decoded errors:', combined_errors)


def normalized_time_spent(combined_actual, combined_decoded, shuffle_id, output_filepath):

    keys = ['u', 'shortcut', 'novel']

    normalized_actual = dict(u=[], shortcut=[], novel=[])
    normalized_decoded = dict(u=[], shortcut=[], novel=[])

    n_sessions = len(combined_actual['together'])

    for val in range(n_sessions):
        actual = dict()
        decode = dict()
        for key in keys:
            actual[key] = combined_actual[key][val]
            decode[key] = combined_decoded[key][val]
        norm_actual = compare_rates(actual)
        norm_decoded = compare_rates(decode)
        for key in keys:
            normalized_actual[key].append(norm_actual[key])
            normalized_decoded[key].append(norm_decoded[key])

    if shuffle_id:
        filename = 'combined-norm_phase3-id_shuffle_decoded.png'
    else:
        filename = 'combined-norm_phase3_decoded.png'
    savepath = os.path.join(output_filepath, filename)

    y_label = 'Points normalized by time spent'
    plot_compare_decoded_track(normalized_actual, normalized_decoded, y_label=y_label, max_y=60., savepath=savepath)


compare_decoded_actual(combined_actual, combined_decoded, combined_track_relative, shuffle_id, pauseB, output_filepath)
# plot_normalized = normalized_time_spent(combined_actual, combined_decoded, n_sessions, shuffle_id, output_filepath)
