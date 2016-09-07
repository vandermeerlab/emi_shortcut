import os
import numpy as np
import matplotlib.pyplot as plt
import pickle
from scipy.interpolate import InterpolatedUnivariateSpline

import vdmlab as vdm

from load_data import get_pos, get_spikes
from tuning_curves_functions import get_tc_1d, find_ideal
from decode_functions import get_edges

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
# import info.R063d4_info as r063d4
# import info.R063d5_info as r063d5
# import info.R063d6_info as r063d6
# import info.R066d1_info as r066d1
# import info.R066d2_info as r066d2
# import info.R066d3_info as r066d3
# import info.R066d4_info as r066d4
# import info.R067d1_info as r067d1

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')

results = []

# infos = [r063d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4, r067d1]

def check_tc_smoothing(smooth_tc, smooth_counts):
# for info in infos:
#     print(info.session_id)
    info = r063d2
    print(smooth_tc, smooth_counts)
    position = get_pos(info.pos_mat, info.pxl_to_cm)
    spikes = get_spikes(info.spike_mat)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= info.run_threshold
    run_pos = position[run_idx]

    track_starts = [info.task_times['phase1'].start, info.task_times['phase2'].start, info.task_times['phase3'].start]
    track_stops = [info.task_times['phase1'].stop, info.task_times['phase2'].stop, info.task_times['phase3'].stop]

    track_pos = run_pos.time_slices(track_starts, track_stops)

    track_spikes = [spiketrain.time_slices(track_starts, track_stops) for spiketrain in spikes]

    binsize = 3
    xedges = np.arange(track_pos.x.min(), track_pos.x.max() + binsize, binsize)
    yedges = np.arange(track_pos.y.min(), track_pos.y.max() + binsize, binsize)

    tuning_curves = vdm.tuning_curve_2d(track_pos, track_spikes, xedges, yedges, gaussian_sigma=smooth_tc)

    counts_binsize = 0.025
    time_edges = get_edges(run_pos, counts_binsize, lastbin=True)
    counts = vdm.get_counts(spikes, time_edges, gaussian_std=smooth_counts)

    decoding_tc = []
    for tuning_curve in tuning_curves:
        decoding_tc.append(np.ravel(tuning_curve))
    decoding_tc = np.array(decoding_tc)

    likelihood = vdm.bayesian_prob(counts, decoding_tc, counts_binsize)

    xcenters = (xedges[1:] + xedges[:-1]) / 2.
    ycenters = (yedges[1:] + yedges[:-1]) / 2.
    xy_centers = vdm.cartesian(xcenters, ycenters)

    time_centers = (time_edges[1:] + time_edges[:-1]) / 2.

    decoded_pos = vdm.decode_location(likelihood, xy_centers, time_centers)
    nan_idx = np.logical_and(np.isnan(decoded_pos.x), np.isnan(decoded_pos.y))
    decoded_pos = decoded_pos[~nan_idx]

    decoded = vdm.remove_teleports(decoded_pos, speed_thresh=10, min_length=3)

    x_spline = InterpolatedUnivariateSpline(track_pos.time, track_pos.x)
    y_spline = InterpolatedUnivariateSpline(track_pos.time, track_pos.y)
    actual_position = vdm.Position(np.hstack((np.clip(x_spline(decoded.time),
                                                      xedges.min(), xedges.max())[..., np.newaxis],
                                             (np.clip(y_spline(decoded.time),
                                                      yedges.min(), yedges.max())[..., np.newaxis]))),
                                   decoded.time)

    errors = actual_position.distance(decoded)
    print('Actual distance:', np.mean(errors))
    return np.mean(errors)

    # plt.plot(actual_position.x, actual_position.y, 'r.', ms=0.7)
    # plt.plot(decoded.x, decoded.y, 'b.')
    # plt.show()

    # test_xy = actual_position.data + np.random.normal(0, 24, actual_position.data.shape)
    # test_pos = vdm.Position(test_xy, actual_position.time)
    # test_errors = actual_position.distance(test_pos)
    # print('Test distance:', np.mean(test_errors))

inputs = []
results = []

smoothing_tc = [None, 0.1, 0.25, 0.5, 1., 3., 5., 7.5, 10., 15.]
smoothing_time = [None, 0.025, 0.05, 0.1, 0.2, 0.5, 1., 2., 5.]
for smooth_tc in smoothing_tc:
    for smooth_t in smoothing_time:
        inputs.append([smooth_tc, smooth_t])
        results.append(check_tc_smoothing(smooth_tc, smooth_t))
print('inputs:', inputs)
print('results:', results)
