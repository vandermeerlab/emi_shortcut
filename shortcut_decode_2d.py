import os
import numpy as np
import pickle
from scipy.interpolate import InterpolatedUnivariateSpline

import vdmlab as vdm

from load_data import get_pos, get_spikes
from tuning_curves_functions import get_tc_1d, find_ideal
from decode_functions import get_edges

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

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


infos = [r063d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4, r067d1]


for info in infos:
    print(info.session_id)
    position = get_pos(info.pos_mat, info.pxl_to_cm)
    spikes = get_spikes(info.spike_mat)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= info.run_threshold
    run_pos = position[run_idx]

    t_start = info.task_times['phase3'].start
    t_stop = info.task_times['phase3'].stop

    sliced_pos = run_pos.time_slice(t_start, t_stop)

    sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

    binsize = 3
    xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
    yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)

    tuning_curves = vdm.tuning_curve_2d(sliced_pos, sliced_spikes, xedges, yedges, gaussian_sigma=0.2)

    counts_binsize = 0.025
    time_edges = get_edges(position, counts_binsize, lastbin=True)
    counts = vdm.get_counts(spikes, time_edges, apply_filter=False)

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

    x_spline = InterpolatedUnivariateSpline(position.time, position.x)
    y_spline = InterpolatedUnivariateSpline(position.time, position.y)
    actual_position = vdm.Position(np.hstack((x_spline(decoded.time)[..., np.newaxis],
                                              (y_spline(decoded.time)[..., np.newaxis]))), decoded.time)

    error = np.abs(decoded.data - actual_position.data)
    avg_error = np.nanmean(error)

    print(avg_error)
