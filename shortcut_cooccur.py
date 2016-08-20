import os
import numpy as np
import vdmlab as vdm

from load_data import get_pos, get_lfp, get_spikes
from tuning_curves_functions import get_tc_1d
from field_functions import unique_fields
from plotting_functions import plot_cooccur

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
import info.R063d4_info as r063d4
import info.R063d5_info as r063d5
import info.R063d6_info as r063d6
import info.R066d1_info as r066d1
import info.R066d3_info as r066d3
import info.R066d2_info as r066d2
import info.R066d3_info as r066d3
import info.R066d4_info as r066d4


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')

infos = [r066d3, r066d4]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]

exp_times = ['pauseA', 'pauseB']
# exp_times = ['pauseA']


# all_probs = dict(active=dict(u=[], shortcut=[], novel=[]), expected=dict(u=[], shortcut=[], novel=[]),
#                  observed=dict(u=[], shortcut=[], novel=[]), zscore=dict(u=[], shortcut=[], novel=[]))
for info in infos:
    print(info.session_id)
    for exp_time in exp_times:
        print(exp_time)

        lfp = get_lfp(info.good_swr[0])
        position = get_pos(info.pos_mat, info.pxl_to_cm)
        spikes = get_spikes(info.spike_mat)

        t_start = info.task_times[exp_time][0]
        t_stop = info.task_times[exp_time][1]

        t_start_idx = vdm.find_nearest_idx(lfp.time, t_start)
        t_end_idx = vdm.find_nearest_idx(lfp.time, t_stop)

        sliced_lfp = lfp[t_start_idx:t_end_idx]

        thresh = (140.0, 250.0)
        swrs = vdm.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=thresh, power_thres=5)

        speed = position.speed(t_smooth=0.5)
        run_idx = np.squeeze(speed.data) >= info.run_threshold
        run_pos = position[run_idx]

        t_start = info.task_times['phase3'][0]
        t_stop = info.task_times['phase3'][1]

        t_start_idx = vdm.find_nearest_idx(run_pos.time, t_start)
        t_stop_idx = vdm.find_nearest_idx(run_pos.time, t_stop)

        sliced_pos = run_pos[t_start_idx:t_stop_idx]

        sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

        tc_filename = info.session_id + '_tuning_1d.pkl'
        pickled_tc = os.path.join(pickle_filepath, tc_filename)

        tuning_curves = get_tc_1d(info, sliced_pos, sliced_spikes, pickled_tc)

        u_fields = vdm.find_fields(tuning_curves['u'], hz_thresh=0.1, min_length=1, max_length=len(tuning_curves['u']))
        shortcut_fields = vdm.find_fields(tuning_curves['shortcut'])
        novel_fields = vdm.find_fields(tuning_curves['novel'])

        u_compare = vdm.find_fields(tuning_curves['u'], hz_thresh=3, min_length=1, max_length=len(tuning_curves['u']),
                                    max_mean_firing=10)
        shortcut_compare = vdm.find_fields(tuning_curves['shortcut'], hz_thresh=3, min_length=1,
                                           max_length=len(tuning_curves['shortcut']), max_mean_firing=10)
        novel_compare = vdm.find_fields(tuning_curves['novel'], hz_thresh=3, min_length=1,
                                        max_length=len(tuning_curves['novel']), max_mean_firing=10)

        u_fields_unique = unique_fields(u_fields, shortcut_compare, novel_compare)
        shortcut_fields_unique = unique_fields(shortcut_fields, u_compare, novel_compare)
        novel_fields_unique = unique_fields(novel_fields, u_compare, shortcut_compare)

        u_fields_single = vdm.get_single_field(u_fields_unique)
        shortcut_fields_single = vdm.get_single_field(shortcut_fields_unique)
        novel_fields_single = vdm.get_single_field(novel_fields_unique)

        u_spikes = []
        for key in u_fields_unique:
            u_spikes.append(spikes[key])

        shortcut_spikes = []
        for key in shortcut_fields_unique:
            shortcut_spikes.append(spikes[key])

        novel_spikes = []
        for key in novel_fields_unique:
            novel_spikes.append(spikes[key])

        swr_intervals = []
        for swr in swrs:
            swr_intervals.append([swr.time[0], swr.time[-1]])
        swr_intervals = np.array(swr_intervals).T

        count_matrix = dict()
        count_matrix['u'] = vdm.spike_counts(u_spikes, swr_intervals, window=0.1)
        count_matrix['shortcut'] = vdm.spike_counts(shortcut_spikes, swr_intervals, window=0.1)
        count_matrix['novel'] = vdm.spike_counts(novel_spikes, swr_intervals, window=0.1)

        probs = dict(active=dict(), expected=dict(), observed=dict(), zscore=dict())
        (probs['active']['u'],
        probs['expected']['u'],
        probs['observed']['u'],
        probs['zscore']['u']) = vdm.compute_cooccur(count_matrix['u'], num_shuffles=10000)

        (probs['active']['shortcut'],
        probs['expected']['shortcut'],
        probs['observed']['shortcut'],
        probs['zscore']['shortcut']) = vdm.compute_cooccur(count_matrix['shortcut'], num_shuffles=10000)

        (probs['active']['novel'],
        probs['expected']['novel'],
        probs['observed']['novel'],
        probs['zscore']['novel']) = vdm.compute_cooccur(count_matrix['novel'], num_shuffles=10000)

        filename = info.session_id + '_cooccur-' + exp_time + '.png'
        savepath = os.path.join(output_filepath, filename)
        plot_cooccur(probs, savepath)

        # all_probs['active']['u'].append(probs['active']['u'])
        # all_probs['expected']['u'].append(probs['expected']['u'])
        # all_probs['observed']['u'].append(probs['observed']['u'])
        # all_probs['zscore']['u'].append(probs['zscore']['u'])
        # all_probs['active']['shortcut'].append(probs['active']['shortcut'])
        # all_probs['expected']['shortcut'].append(probs['expected']['shortcut'])
        # all_probs['observed']['shortcut'].append(probs['observed']['shortcut'])
        # all_probs['zscore']['shortcut'].append(probs['zscore']['shortcut'])
        # all_probs['active']['novel'].append(probs['active']['novel'])
        # all_probs['expected']['novel'].append(probs['expected']['novel'])
        # all_probs['observed']['novel'].append(probs['observed']['novel'])
        # all_probs['zscore']['novel'].append(probs['zscore']['novel'])

        filename = 'combined_cooccur-' + exp_time + '.png'
        savepath = os.path.join(output_filepath, filename)
        plot_cooccur(probs, savepath)