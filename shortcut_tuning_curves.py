import os
import numpy as np
import pickle

import vdmlab as vdm

from load_data import get_pos, get_spikes
from tuning_curves_functions import get_tc_1d, get_odd_firing_idx
from plotting_functions import plot_sorted_tc

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


infos = [r063d4]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'tuning')

lets_2d = False

if lets_2d:
    for info in infos:
        print(info.session_id)

        tc_filename = info.session_id + '_tuning_2d.pkl'
        pickled_tc = os.path.join(pickle_filepath, tc_filename)
        if os.path.isfile(pickled_tc):
            with open(pickled_tc, 'rb') as fileobj:
                tuning_curves = pickle.load(fileobj)
        else:
            position = get_pos(info.pos_mat, info.pxl_to_cm)
            spikes = get_spikes(info.spike_mat)

            speed = position.speed(t_smooth=0.5)
            run_idx = np.squeeze(speed.data) >= info.run_threshold
            run_pos = position[run_idx]

            t_start = info.task_times['phase3'][0]
            t_stop = info.task_times['phase3'][1]

            sliced_pos = run_pos.time_slice(t_start, t_stop)

            sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

            binsize = 3
            xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
            yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)

            tuning_curves = vdm.tuning_curve_2d(sliced_pos, sliced_spikes, xedges, yedges, gaussian_sigma=0.2)

            # with open(pickled_tc, 'wb') as fileobj:
            #     pickle.dump(tuning_curves, fileobj)

        import matplotlib.pyplot as plt
        position = get_pos(info.pos_mat, info.pxl_to_cm)
        binsize = 3
        xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
        yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)
        xx, yy = np.meshgrid(xedges, yedges)
        for tuning_curve in tuning_curves[0:3]:
            pp = plt.pcolormesh(xx, yy, tuning_curve, cmap='YlGn')
            plt.colorbar(pp)
            plt.axis('off')
            plt.show()

else:
    for info in infos:
        print(info.session_id)
        tc_filename = info.session_id + '_tuning_1d.pkl'
        pickled_tc = os.path.join(pickle_filepath, tc_filename)
        if os.path.isfile(pickled_tc):
            with open(pickled_tc, 'rb') as fileobj:
                tuning_curves = pickle.load(fileobj)
        else:
            position = get_pos(info.pos_mat, info.pxl_to_cm)
            spikes = get_spikes(info.spike_mat)

            speed = position.speed(t_smooth=0.5)
            run_idx = np.squeeze(speed.data) >= info.run_threshold
            run_pos = position[run_idx]

            t_start = info.task_times['phase3'][0]
            t_stop = info.task_times['phase3'][1]

            sliced_pos = run_pos.time_slice(t_start, t_stop)

            sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

            tuning_curves = get_tc_1d(info, sliced_pos, sliced_spikes, pickled_tc)

            sort_idx = dict()
            odd_firing_idx = dict()
            sorted_tc = dict(u=[], shortcut=[], novel=[])

            for key in tuning_curves:
                sort_idx[key] = vdm.get_sort_idx(tuning_curves[key])
                odd_firing_idx[key] = get_odd_firing_idx(tuning_curves[key], max_mean_firing=10)

                for idx in sort_idx[key]:
                    if idx not in odd_firing_idx[key]:
                        sorted_tc[key].append(tuning_curves[key][idx])

                filename = info.session_id + '-sorted_tc-' + key + '.png'
                savepath = os.path.join(output_filepath, filename)
                plot_sorted_tc(sorted_tc[key], savepath)
