import os
import numpy as np
import pickle
import vdmlab as vdm

from load_data import get_pos, get_spikes
from field_functions import unique_fields
from tuning_curves_functions import get_tc_1d
from plotting_functions import plot_fields

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
output_filepath = os.path.join(thisdir, 'plots', 'fields')


# infos = [r063d4]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4, r067d1]

for info in infos:
    print(info.session_id)

    tc_filename = info.session_id + '_tuning_1d.pkl'
    pickled_tc = os.path.join(pickle_filepath, tc_filename)

    position = get_pos(info.pos_mat, info.pxl_to_cm)
    spikes = get_spikes(info.spike_mat)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= info.run_threshold
    run_pos = position[run_idx]

    t_start = info.task_times['phase3'].start
    t_stop = info.task_times['phase3'].stop

    sliced_pos = run_pos.time_slice(t_start, t_stop)

    sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

    tuning_curves = get_tc_1d(info, sliced_pos, sliced_spikes, pickled_tc)

    heatmap_filename = info.session_id + '_spike_heatmaps.pkl'
    pickled_spike_heatmaps = os.path.join(pickle_filepath, heatmap_filename)
    if os.path.isfile(pickled_spike_heatmaps):
        with open(pickled_spike_heatmaps, 'rb') as fileobj:
            spike_heatmaps = pickle.load(fileobj)
    else:
        all_neurons = list(range(0, len(spikes)))
        spike_heatmaps = vdm.get_heatmaps(all_neurons, spikes, position)
        with open(pickled_spike_heatmaps, 'wb') as fileobj:
            pickle.dump(spike_heatmaps, fileobj)

    u_fields = vdm.find_fields(tuning_curves['u'])
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

    print('U: Of', str(len(u_fields)), 'fields,',
          str(len(u_fields_unique)), 'are unique, with',
          str(len(u_fields_single)), 'with single peaks.')
    print('Shortcut: Of', str(len(shortcut_fields)), 'fields,',
          str(len(shortcut_fields_unique)), 'are unique, with',
          str(len(shortcut_fields_single)), 'with single peaks.')
    print('Novel: Of', str(len(novel_fields)), 'fields,',
          str(len(novel_fields_unique)), 'are unique, with',
          str(len(novel_fields_single)), 'with single peaks.')

    num_bins = 100

    all_trajectories = dict(u=u_fields, shortcut=shortcut_fields, novel=novel_fields)

    for trajectory in all_trajectories:
        all_heatmaps = np.zeros((num_bins, num_bins))
        for key in all_trajectories[trajectory]:
            all_heatmaps += spike_heatmaps[key]
        num_neurons = len(all_trajectories[trajectory])

        filename = info.session_id + '-fields_' + str(trajectory) + '.png'
        savepath = os.path.join(output_filepath, filename)
        plot_fields(all_heatmaps, position, num_neurons, savepath)

# for key in novel_fields_unique:
#     print('plotting neuron ' + str(key))
#     num_neurons = 1
#     savepath = output_filepath
#     plot_fields(spike_heatmaps[key], pos, num_neurons, savepath, savefig=False)
