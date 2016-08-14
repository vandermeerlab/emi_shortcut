import os
import numpy as np

import vdmlab as vdm

from load_data import get_pos, get_csc, get_spikes
from tuning_curves_functions import get_tc, linearize

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
import info.R063d4_info as r063d4
import info.R063d5_info as r063d5
import info.R063d6_info as r063d6
import info.R066d1_info as r066d1
import info.R066d2_info as r066d2
import info.R066d3_info as r066d3
import info.R066d4_info as r066d4

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


infos = [r063d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]


for info in infos:
    print(info.session_id)
    pos = get_pos(info.pos_mat, info.pxl_to_cm)

    t_start = info.task_times['phase2'][0]
    t_stop = info.task_times['phase2'][1]

    t_start_idx = vdm.find_nearest_idx(pos['time'], t_start)
    t_end_idx = vdm.find_nearest_idx(pos['time'], t_stop)

    sliced_pos = dict()
    sliced_pos['x'] = pos['x'][t_start_idx:t_end_idx]
    sliced_pos['y'] = pos['y'][t_start_idx:t_end_idx]
    sliced_pos['time'] = pos['time'][t_start_idx:t_end_idx]

    linear, zone = linearize(info, pos)

    spikes = get_spikes(info.spike_mat)

    tc = get_tc(info, pos, pickle_filepath)

    linear = linear['u']
    tc = np.array(tc['u'])

    binsize = np.median(np.diff(linear['time']))
    edges = np.hstack((linear['time']-(binsize/2), linear['time'][-1]))
    subsample = 6
    edges = edges[::subsample]
    counts = vdm.get_counts(spikes['time'], edges)

    # plt.pcolormesh(counts[:,:100])
    # plt.colorbar()
    # plt.show()

    prob = vdm.bayesian_prob(counts, tc, binsize)

    # plt.pcolormesh(prob[200::-1])
    # plt.colorbar()
    # plt.show()

    decoded_position = vdm.decode_location(prob, linear)

    decoded = dict()
    decoded['time'] = edges[:-1] + np.median(np.diff(edges))/2
    decoded['position'] = decoded_position

    actual_idx = vdm.find_nearest_indices(linear['time'], decoded['time'])
    actual_location = linear['position'][actual_idx]

    # decoded[np.isnan(decoded)] = 0
    # decode_error = np.abs(actual_location - decoded)
    # print(np.mean(decode_error))
    #
    # plt.plot(centers, decoded)
    # plt.plot(linear['time'], linear['position'], 'r.')
    # plt.show()

    sequences = vdm.decoded_sequences(decoded)

    avg_error = []
    decoded['position'][np.isnan(decoded['position'])] = 0
    for seq in sequences['index']:
        decode_error = np.abs(actual_location[seq[0]:seq[1]] - decoded['position'][seq[0]:seq[1]])
        avg_error.append(np.mean(decode_error))
    print(np.mean(avg_error))

    # plt.plot(linear['time'], linear['position'], 'r.')
    # for seq in sequences['index']:
    #     plt.plot(decoded['time'][seq[0]:seq[1]], decoded['position'][seq[0]:seq[1]], 'b.')
    # plt.show()
