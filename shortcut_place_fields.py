import os
import numpy as np
import pickle
import vdmlab as vdm

from field_functions import unique_fields
from tuning_curves_functions import get_tc
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


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'fields')


# infos = [r063d4]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]

for info in infos:
    print(info.session_id)
    pos = info.get_pos(info.pxl_to_cm)

    tc = get_tc(info, pos, pickle_filepath)

    heatmap_filename = info.session_id + '_spike_heatmaps.pkl'
    pickled_spike_heatmaps = os.path.join(pickle_filepath, heatmap_filename)
    if os.path.isfile(pickled_spike_heatmaps):
        with open(pickled_spike_heatmaps, 'rb') as fileobj:
            spike_heatmaps = pickle.load(fileobj)
    else:
        spikes = info.get_spikes()

        all_neurons = list(range(0, len(spikes['time'])))
        spike_heatmaps = vdm.get_heatmaps(all_neurons, spikes, pos)
        with open(pickled_spike_heatmaps, 'wb') as fileobj:
            pickle.dump(spike_heatmaps, fileobj)

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
        plot_fields(all_heatmaps, pos, num_neurons, savepath)

# for key in novel_fields_unique:
#     print('plotting neuron ' + str(key))
#     num_neurons = 1
#     savepath = output_filepath
#     plot_fields(spike_heatmaps[key], pos, num_neurons, savepath, savefig=False)
