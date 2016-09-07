import os
import numpy as np
import random
import matplotlib.pyplot as plt
import pickle
from scipy.interpolate import InterpolatedUnivariateSpline

import vdmlab as vdm

from load_data import get_pos, get_spikes
from maze_functions import find_zones
from decode_functions import get_edges, point_in_zones
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
import info.R067d1_info as r067d1
import info.R067d2_info as r067d2
import info.R067d3_info as r067d3
import info.R067d4_info as r067d4
import info.R067d5_info as r067d5
import info.R068d1_info as r068d1
import info.R068d2_info as r068d2
import info.R068d3_info as r068d3
import info.R068d4_info as r068d4

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')

# results = []

# infos = [r063d2, r063d3]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6,
         r066d1, r066d2, r066d3, r066d4,
         r067d1, r067d2, r067d3, r067d4, r067d5,
         r068d1, r068d2, r068d3, r068d4]

for info in infos:
    print(info.session_id)
    position = get_pos(info.pos_mat, info.pxl_to_cm)
    spikes = get_spikes(info.spike_mat)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= info.run_threshold
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

    tuning_curves = vdm.tuning_curve_2d(track_pos, track_spikes, xedges, yedges, gaussian_sigma=0.25)
    random.shuffle(tuning_curves)

    counts_binsize = 0.025
    time_edges = get_edges(run_pos, counts_binsize, lastbin=True)
    counts = vdm.get_counts(track_spikes, time_edges, gaussian_std=0.025)

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

    filename = info.session_id + '-phase3-id_shuffle_decoded.png'
    savepath = os.path.join(output_filepath, filename)

    plot_compare_decoded_track(actual_zones, decoded_zones, str(round(np.mean(errors), 2)), savepath)

    print('Total number of decoded points:', (len(decoded_zones['u'].time) + len(decoded_zones['shortcut'].time) +
                                      len(decoded_zones['novel'].time) + len(decoded_zones['other'].time)))

# inputs = []
# results = []
#
# smoothing_tc = [None, 0.1, 0.25, 0.5, 1., 3., 5., 7.5, 10., 15.]
# smoothing_time = [None, 0.025, 0.05, 0.1, 0.2, 0.5, 1., 2., 5.]
# for smooth_tc in smoothing_time:
#     for smooth_t in smoothing_tc:
#         inputs.append([smooth_tc, smooth_t])
#         results.append(check_tc_smoothing(smooth_tc, smooth_t))
# print('inputs:', inputs)
# print('results:', results)
