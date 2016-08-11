import os
import vdmlab as vdm

from load_data import get_pos, get_csc, get_spikes
from tuning_curves_functions import get_tc
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
import info.R066d4_info as r066d4


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')

infos = [r066d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]

# exp_times = ['pauseA', 'pauseB']
exp_times = ['pauseA']
for info in infos:

    for exp_time in exp_times:
        print(exp_time)
        csc = get_csc(info.good_swr[0])
        pos = get_pos(info.pos_mat, info.pxl_to_cm)
        spikes = get_spikes(info.spike_mat)

        t_start = info.task_times[exp_time][0]
        t_stop = info.task_times[exp_time][0]+800

        t_start_idx = vdm.find_nearest_idx(csc['time'], t_start)
        t_end_idx = vdm.find_nearest_idx(csc['time'], t_stop)

        sliced_csc = dict()
        sliced_csc['time'] = csc['time'][t_start_idx:t_end_idx]
        sliced_csc['data'] = csc['data'][t_start_idx:t_end_idx]

        swr_times, swr_idx, filtered_butter = vdm.detect_swr_hilbert(sliced_csc, fs=info.fs, power_thres=5)

        tc = get_tc(info, pos, pickle_filepath)

        u_fields = vdm.find_fields(tc['u'], hz_thresh=0.1, min_length=1, max_length=len(tc['u']))
        shortcut_fields = vdm.find_fields(tc['shortcut'])
        novel_fields = vdm.find_fields(tc['novel'])

        u_compare = vdm.find_fields(tc['u'], hz_thresh=3, min_length=1, max_length=len(tc['u']),
                                    max_mean_firing=10)
        shortcut_compare = vdm.find_fields(tc['shortcut'], hz_thresh=3, min_length=1, max_length=len(tc['shortcut']),
                                           max_mean_firing=10)
        novel_compare = vdm.find_fields(tc['novel'], hz_thresh=3, min_length=1, max_length=len(tc['novel']),
                                        max_mean_firing=10)

        u_fields_unique = unique_fields(u_fields, shortcut_compare, novel_compare)
        shortcut_fields_unique = unique_fields(shortcut_fields, u_compare, novel_compare)
        novel_fields_unique = unique_fields(novel_fields, u_compare, shortcut_compare)

        u_fields_single = vdm.get_single_field(u_fields_unique)
        shortcut_fields_single = vdm.get_single_field(shortcut_fields_unique)
        novel_fields_single = vdm.get_single_field(novel_fields_unique)

        u_spikes = dict(time=[], label=[])
        for key in u_fields_unique:
            u_spikes['time'].append(spikes['time'][key])
            u_spikes['label'].append(spikes['label'][key])

        shortcut_spikes = dict(time=[], label=[])
        for key in shortcut_fields_unique:
            shortcut_spikes['time'].append(spikes['time'][key])
            shortcut_spikes['label'].append(spikes['label'][key])

        novel_spikes = dict(time=[], label=[])
        for key in novel_fields_unique:
            novel_spikes['time'].append(spikes['time'][key])
            novel_spikes['label'].append(spikes['label'][key])

        count_matrix = dict()
        count_matrix['u'] = vdm.spike_counts(u_spikes, swr_times, window=0.1)
        count_matrix['shortcut'] = vdm.spike_counts(shortcut_spikes, swr_times, window=0.1)
        count_matrix['novel'] = vdm.spike_counts(novel_spikes, swr_times, window=0.1)

        probs = dict(active=dict(), expected=dict(), observed=dict(), zscore=dict())
        probs['active']['u'], \
        probs['expected']['u'], \
        probs['observed']['u'], \
        probs['zscore']['u'] = vdm.compute_cooccur(count_matrix['u'], num_shuffles=10000)

        probs['active']['shortcut'], \
        probs['expected']['shortcut'], \
        probs['observed']['shortcut'], \
        probs['zscore']['shortcut'] = vdm.compute_cooccur(count_matrix['shortcut'], num_shuffles=10000)

        probs['active']['novel'], \
        probs['expected']['novel'], \
        probs['observed']['novel'], \
        probs['zscore']['novel'] = vdm.compute_cooccur(count_matrix['novel'], num_shuffles=10000)

        filename = info.session_id + '_cooccur-' + exp_time + '.png'
        savepath = os.path.join(output_filepath, filename)
        plot_cooccur(probs, savepath)
