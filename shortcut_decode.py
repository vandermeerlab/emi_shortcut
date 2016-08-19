import os
import numpy as np
import pickle

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

    t_start = info.task_times['phase3'][0]
    t_stop = info.task_times['phase3'][1]

    t_start_idx = vdm.find_nearest_idx(run_pos.time, t_start)
    t_stop_idx = vdm.find_nearest_idx(run_pos.time, t_stop)

    sliced_pos = run_pos[t_start_idx:t_stop_idx]

    sliced_spikes = dict()
    sliced_spikes['time'] = vdm.time_slice(spikes['time'], t_start, t_stop)

    linear, zone = find_ideal(info, sliced_pos, expand_by=2)

    tc_filename = info.session_id + '_tuning_1d.pkl'
    pickled_tc = os.path.join(pickle_filepath, tc_filename)
    # if os.path.isfile(pickled_tc):
    #     with open(pickled_tc, 'rb') as fileobj:
    #         tuning_curves = pickle.load(fileobj)
    # else:
    tuning_curves = get_tc_1d(info, sliced_pos, sliced_spikes, pickled_tc)

    linear = linear['u']
    tuning_curves = tuning_curves['u']

    counts_binsize = 0.025

    edges = get_edges(linear, counts_binsize, lastbin=True)
    counts = vdm.get_counts(spikes['time'], edges)

    likelihood = vdm.bayesian_prob(counts, tuning_curves, counts_binsize)

    decoded_pos = vdm.decode_location(likelihood, linear)

    decoded_time = edges[:-1] + (counts_binsize/2)
    decoded = vdm.Position(decoded_pos, decoded_time)

    decoded_sequence = vdm.filter_jumps(decoded)

    actual_idx = vdm.find_nearest_indices(linear.time, decoded_sequence.time)
    decode_error = np.abs(linear.x[actual_idx] - decoded_sequence.x)

    print(np.mean(decode_error), np.median(decode_error), np.min(decode_error), np.max(decode_error))

    import matplotlib.pyplot as plt
    plt.plot(linear.time[actual_idx], linear.x[actual_idx], 'r.')
    plt.plot(decoded_sequence.time, decoded_sequence.x, 'b.')
    plt.show()
