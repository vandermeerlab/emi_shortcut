import os
import numpy as np
import matplotlib.pyplot as plt
import pickle
from scipy.interpolate import InterpolatedUnivariateSpline

import vdmlab as vdm

from loading_data import get_data
from analyze_tuning_curves import get_tc_1d, find_ideal
from analyze_decode import get_edges

# import info.R063d2_info as r063d2
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


infos = [r063d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4, r067d1]


for info in infos:
    print(info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= info.run_threshold
    run_pos = position[run_idx]

    t_start = info.task_times['phase3'].start
    t_stop = info.task_times['phase3'].stop

    sliced_pos = run_pos.time_slice(t_start, t_stop)

    sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

    linear, zone = find_ideal(info, sliced_pos, expand_by=2)

    tc_filename = info.session_id + '_tuning_1d.pkl'
    pickled_tc = os.path.join(pickle_filepath, tc_filename)
    # if os.path.isfile(pickled_tc):
    #     with open(pickled_tc, 'rb') as fileobj:
    #         tuning_curves = pickle.load(fileobj)
    # else:
    pos_binsize = 3
    tuning_curves = get_tc_1d(info, sliced_pos, sliced_spikes, pickled_tc, binsize=pos_binsize)

    linear = linear['u']
    tuning_curves = tuning_curves['u']

    counts_binsize = 0.025

    time_edges = get_edges(linear, counts_binsize, lastbin=True)
    counts = vdm.get_counts(spikes, time_edges, gaussian_std=counts_binsize)

    likelihood = vdm.bayesian_prob(counts, tuning_curves, counts_binsize)

    pos_edges = vdm.binned_position(linear, pos_binsize)
    x_centers = (pos_edges[1:] + pos_edges[:-1]) / 2.
    x_centers = x_centers[..., np.newaxis]

    time_centers = (time_edges[1:] + time_edges[:-1]) / 2.

    decoded_pos = vdm.decode_location(likelihood, x_centers, time_centers)
    nan_idx = np.isnan(decoded_pos.x)
    decoded_pos = decoded_pos[~nan_idx]

    decoded = vdm.remove_teleports(decoded_pos, speed_thresh=5, min_length=2)

    spline = InterpolatedUnivariateSpline(linear.time, linear.x)
    actual_position = vdm.Position(np.clip(spline(decoded.time), pos_edges.min(), pos_edges.max()), decoded.time)

    errors = actual_position.distance(decoded)
    print('Average error distance:', np.mean(errors))

    # plt.plot(actual_position.time, actual_position.x, 'r.')
    # plt.plot(decoded.time, decoded.x, 'b.')
    # plt.show()
