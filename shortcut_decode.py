import os
import numpy as np
import random
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import pickle
from scipy.interpolate import InterpolatedUnivariateSpline

import vdmlab as vdm

from load_data import get_pos, get_spikes
from maze_functions import find_zones
from decode_functions import get_edges, point_in_zones, compare_rates, compare_lengths
from plotting_functions import (plot_decoded, plot_decoded_pause, plot_decoded_errors,
                                plot_compare_decoded_pauses)

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
import info.R066d6_info as r066d6
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
import info.R068d6_info as r068d6


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


def get_decoded(infos, experiment_time='tracks', shuffle_id=False):
    """Finds combined decoded from all sessions.

    Parameters
    ----------
    info: list of modules
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
    total_times = []
    combined_errors = []
    combined_lengths = dict(u=[], shortcut=[], novel=[], other=[], together=[])
    combined_decoded = dict(u=[], shortcut=[], novel=[], other=[], together=[])

    for info in infos:
        print(info.session_id)
        position = get_pos(info.pos_mat, info.pxl_to_cm)
        spikes = get_spikes(info.spike_mat)

        speed = position.speed(t_smooth=0.5)
        run_idx = np.squeeze(speed.data) >= 0.1
        run_pos = position[run_idx]

        track_starts = [info.task_times['phase1'].start,
                        info.task_times['phase2'].start,
                        info.task_times['phase3'].start]
        track_stops = [info.task_times['phase1'].stop,
                       info.task_times['phase2'].stop,
                       info.task_times['phase3'].stop]

        # track_start = info.task_times['phase3'].start
        # track_stop = info.task_times['phase3'].stop

        track_pos = run_pos.time_slices(track_starts, track_stops)

        track_spikes = [spiketrain.time_slices(track_starts, track_stops) for spiketrain in spikes]

        binsize = 3
        xedges = np.arange(track_pos.x.min(), track_pos.x.max() + binsize, binsize)
        yedges = np.arange(track_pos.y.min(), track_pos.y.max() + binsize, binsize)

        tuning_curves = vdm.tuning_curve_2d(track_pos, track_spikes, xedges, yedges, gaussian_sigma=0.1)

        if shuffle_id:
            random.shuffle(tuning_curves)

        if experiment_time == 'tracks':
            decode_spikes = track_spikes
        else:
            decode_spikes = [spiketrain.time_slice(info.task_times[experiment_time].start,
                                                   info.task_times[experiment_time].stop) for spiketrain in spikes]

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

        total_times.append(len(time_edges) - 1)

        combined_errors.extend(errors)

        combined_lengths['u'].append(LineString(info.u_trajectory).length)
        combined_lengths['shortcut'].append(LineString(info.shortcut_trajectory).length)
        combined_lengths['novel'].append(LineString(info.novel_trajectory).length)

        # combined_actual['u'].append(actual_zones['u'])
        # combined_actual['shortcut'].append(actual_zones['shortcut'])
        # combined_actual['novel'].append(actual_zones['novel'])
        # combined_actual['other'].append(actual_zones['other'])
        # combined_actual['together'].append(len(actual_zones['u'].time) + len(actual_zones['shortcut'].time) +
        #                                    len(actual_zones['novel'].time) + len(actual_zones['other'].time))

        combined_decoded['u'].append(decoded_zones['u'])
        combined_decoded['shortcut'].append(decoded_zones['shortcut'])
        combined_decoded['novel'].append(decoded_zones['novel'])
        combined_decoded['other'].append(decoded_zones['other'])
        combined_decoded['together'].append(len(decoded_zones['u'].time) + len(decoded_zones['shortcut'].time) +
                                            len(decoded_zones['novel'].time) + len(decoded_zones['other'].time))

    return combined_decoded, combined_errors, total_times, combined_lengths


# def compare_decoded_actual(combined_actual, combined_decoded, shuffle_id, output_filepath, pause=None):
#     keys = ['u', 'shortcut', 'novel']
#
#     actual = dict(u=[], shortcut=[], novel=[])
#     decode = dict(u=[], shortcut=[], novel=[])
#
#     n_sessions = len(combined_actual['together'])
#
#     # length_tracks = info.track_length['u'] + info.track_length['shortcut'] + info.track_length['novel']
#
#     for key in keys:
#         if len(combined_actual['together']) != len(combined_decoded['together']):
#             raise ValueError("must have same number of decoded and actual samples")
#
#         for val in range(n_sessions):
#             actual[key].append(len(combined_actual[key][val].time)/combined_actual['together'][val])
#             decode[key].append(len(combined_decoded[key][val].time)/combined_decoded['together'][val])
#
#     if shuffle_id and pause is None:
#         filename = 'combined-phase3-id_shuffle_decoded.png'
#     elif shuffle_id and pause is not None:
#         filename = 'combined-' + pause + '-id_shuffle_decoded.png'
#     elif pause is not None and not shuffle_id:
#         filename = 'combined-' + pause + '_decoded.png'
#     elif not shuffle_id and pause is None:
#         filename = 'combined-phase3_decoded.png'
#     else:
#         filename = 'unknown_combination.png'
#     savepath = os.path.join(output_filepath, filename)
#
#     if pause is not None:
#         plot_compare_decoded_track(decode, max_y=1.0, savepath=savepath)
#     else:
#         plot_compare_decoded_track(decode, actual, distance=str(round(np.mean(combined_errors), 2)),
#                                    max_y=1.0, savepath=savepath)
#
#     print('Decoded errors:', combined_errors)


def normalized_time_spent(combined_decoded, n_sessions, lengths):
    decoded_linger = dict(u=[], shortcut=[], novel=[])
    decoded_length = dict(u=[], shortcut=[], novel=[])
    for val in range(n_sessions):
        decode = dict()
        length = dict()
        for key in decoded_linger:
            decode[key] = combined_decoded[key][val]
            length[key] = lengths[key][val]
        norm_decoded = compare_rates(decode)
        len_decoded = compare_lengths(decode, length)
        for key in decoded_linger:
            decoded_linger[key].append(norm_decoded[key])
            decoded_length[key].append(len_decoded[key])

    filename = 'combined-time-norm_tracks_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    y_label = 'Points normalized by time spent'
    plot_decoded(decoded_linger, y_label=y_label, max_y=None, savepath=savepath)

    filename = 'combined-length-norm_tracks_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    y_label = 'Points normalized by track length'
    plot_decoded(decoded_length, y_label=y_label, max_y=None, savepath=savepath)


# infos = [r063d2, r063d3]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6,
         r066d1, r066d2, r066d3, r066d4, r066d5, r066d6,
         r067d1, r067d2, r067d3, r067d4, r067d5,
         r068d1, r068d2, r068d3, r068d4, r068d5, r068d6]
# infos = [r068d1, r068d2, r068d3, r068d4, r068d5, r068d6]


# Plot decoding errors during track times
if 1:
    combined_decoded, combined_errors, total_times, lengths = get_decoded(infos, shuffle_id=False)
    print('Mean decoded errors:', np.mean(combined_errors))
    shuffled_decoded, shuffled_errors, shuffled_times, shuffled_lengths = get_decoded(infos, shuffle_id=True)
    print('Mean shuffled errors:', np.mean(combined_errors))
    filename = 'combined-errors_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_errors(combined_errors, shuffled_errors, fliersize=3, savepath=savepath)

# Plot proportion of pauseA and pauseB spent in each trajectory
if 0:
    experiment_time = 'pauseA'
    decoded_pausea, errors_pausea, times_pausea, lengths_pausea = get_decoded(infos, experiment_time, shuffle_id=False)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_pausea, times_pausea, savepath=savepath)

    experiment_time = 'pauseB'
    decoded_pauseb, errors_pauseb, times_pauseb, lengths_pauseb = get_decoded(infos, experiment_time, shuffle_id=False)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_pauseb, times_pauseb, savepath=savepath)

    filename = 'combined-pauses_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_compare_decoded_pauses(decoded_pausea, times_pausea, decoded_pauseb, times_pauseb, ['Pause A', 'Pause B'],
                                savepath=savepath)

# Plot proportion of pauseA and pauseB spent in each trajectory
if 0:
    experiment_time = 'phase2'
    decoded_phase1, errors_phase1, times_phase1, lengths_phase1 = get_decoded(infos, experiment_time, shuffle_id=False)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_phase1, times_phase1, savepath=savepath)

    experiment_time = 'phase3'
    decoded_phase3, errors_phase3, times_phase3, lengths_phase3 = get_decoded(infos, experiment_time, shuffle_id=False)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_phase3, times_phase3, savepath=savepath)

    filename = 'combined-phases_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_compare_decoded_pauses(decoded_phase1, times_phase1, decoded_phase3, times_phase3, ['Phase 2', 'Phase 3'],
                                savepath=savepath)

# Plot decoding normalized by time spent
if 0:
    combined_decoded, combined_errors, total_times, lengths = get_decoded(infos, shuffle_id=False)
    n_sessions = len(infos)
    normalized_time_spent(combined_decoded, n_sessions, lengths)
