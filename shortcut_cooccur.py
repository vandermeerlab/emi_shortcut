import os
import numpy as np

import vdmlab as vdm

from load_data import get_pos, get_spikes, get_lfp
from field_functions import get_unique_fields, categorize_fields
from maze_functions import find_zones
from plotting_functions import plot_cooccur, plot_cooccur_combined

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
import info.R068d6_info as r068d6


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')

# infos = [r063d2, r063d3]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6,
         r066d1, r066d2, r066d3, r066d4, r066d5,
         r067d1, r067d2, r067d3, r067d4, r067d5,
         r068d1, r068d2, r068d3, r068d4, r068d5, r068d6]

experiment_times = ['pauseA', 'pauseB']

def get_cooccur(infos, experiment_times):
    field_thresh = 1.
    power_thresh = 5.
    z_thresh = 3.
    merge_thresh = 0.02
    min_length = 0.01

    for experiment_time in experiment_times:
        print(experiment_time)



        # total_epochs = 0
        n_epochs = []
        all_probs = []

        for info in infos:
            print(info.session_id)

            lfp = get_lfp(info.good_swr[0])
            position = get_pos(info.pos_mat, info.pxl_to_cm)
            spikes = get_spikes(info.spike_mat)

            speed = position.speed(t_smooth=0.5)
            run_idx = np.squeeze(speed.data) >= 0.1
            run_pos = position[run_idx]

            t_start_tc = info.task_times['phase3'].start
            t_stop_tc = info.task_times['phase3'].stop

            tc_pos = run_pos.time_slice(t_start_tc, t_stop_tc)

            tc_spikes = [spiketrain.time_slice(t_start_tc, t_stop_tc) for spiketrain in spikes]

            binsize = 3
            xedges = np.arange(tc_pos.x.min(), tc_pos.x.max() + binsize, binsize)
            yedges = np.arange(tc_pos.y.min(), tc_pos.y.max() + binsize, binsize)

            tuning_curves = vdm.tuning_curve_2d(tc_pos, tc_spikes, xedges, yedges, gaussian_sigma=0.1)

            zones = find_zones(info)

            fields_tunings = categorize_fields(tuning_curves, zones, xedges, yedges, field_thresh=field_thresh)

            keys = ['u', 'shortcut', 'novel']
            unique_fields = dict()
            unique_fields['u'] = get_unique_fields(fields_tunings['u'],
                                                   fields_tunings['shortcut'],
                                                   fields_tunings['novel'])
            unique_fields['shortcut'] = get_unique_fields(fields_tunings['shortcut'],
                                                          fields_tunings['novel'],
                                                          fields_tunings['u'])
            unique_fields['novel'] = get_unique_fields(fields_tunings['novel'],
                                                       fields_tunings['u'],
                                                       fields_tunings['shortcut'])

            field_spikes = dict(u=[], shortcut=[], novel=[])
            for field in unique_fields.keys():
                for key in unique_fields[field]:
                    field_spikes[field].append(spikes[key])

            t_start = info.task_times[experiment_time].start
            t_stop = info.task_times[experiment_time].stop

            sliced_lfp = lfp.time_slice(t_start, t_stop)

            sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

            swrs = vdm.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                          power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

            multi_swrs = vdm.find_multi_in_epochs(spikes, swrs, min_involved=3)

            n_epochs.append(multi_swrs.n_epochs)

            count_matrix = dict()
            for key in field_spikes:
                count_matrix[key] = vdm.spike_counts(field_spikes[key], multi_swrs)

            tetrode_mask = dict()
            for key in field_spikes:
                tetrode_mask[key] = vdm.get_tetrode_mask(field_spikes[key])

            probs = dict()
            for key in count_matrix:
                probs[key] = vdm.compute_cooccur(count_matrix[key], tetrode_mask[key], num_shuffles=10000)

            all_probs.append(probs)

            return all_probs, n_epochs
            # filename = 'testing_cooccur-' + experiment_time + '.png'
            # savepath = os.path.join(output_filepath, filename)
            # plot_cooccur(probs, savepath=None)

all_probs, n_epochs = get_cooccur(infos, experiment_times)

total_epochs = np.sum(n_epochs)

combined_weighted = dict(u=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                         shortcut=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                         novel=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]))
combined = dict(u=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                shortcut=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                novel=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]))

keys = ['u', 'shortcut', 'novel']
for trajectory in combined:
    for key in combined[trajectory]:
        if np.sum(probs[trajectory][key]) > 0:
            combined_weighted[trajectory][key].append(np.nanmean(probs[trajectory][key]) * multi_swrs.n_epochs)
            combined[trajectory][key].extend(probs[trajectory][key])
        else:
            combined_weighted[trajectory][key].append(0.0)
            combined[trajectory][key].append(0.0)

filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '.png'
savepath_weighted = os.path.join(output_filepath, filename_weighted)
plot_cooccur_combined(combined_weighted, total_epochs, savepath_weighted)

filename = 'combined_cooccur-' + experiment_time + '.png'
savepath = os.path.join(output_filepath, filename)
plot_cooccur(combined, savepath)
