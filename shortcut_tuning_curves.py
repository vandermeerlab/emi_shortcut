import os
import numpy as np
import pickle

import vdmlab as vdm

from load_data import get_pos, get_spikes
from tuning_curves_functions import get_tc, get_odd_firing_idx, tuning_curve_2d
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


infos = [r063d3]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'tuning')

lets_2d = True

if lets_2d:
    for info in infos:
        print(info.session_id)
        tc_filename = info.session_id + '_tuning_2d.pkl'
        pickled_tc = os.path.join(pickle_filepath, tc_filename)
        if os.path.isfile(pickled_tc):
            with open(pickled_tc, 'rb') as fileobj:
                tuning_curves = pickle.load(fileobj)
        else:
            pos = get_pos(info.pos_mat, info.pxl_to_cm)
            spikes = get_spikes(info.spike_mat)

            binsize = 3
            xedges = np.arange(pos['x'].min(), pos['x'].max()+binsize, binsize)
            yedges = np.arange(pos['y'].min(), pos['y'].max()+binsize, binsize)

            speed = vdm.get_speed(pos)
            t_run = speed['time'][speed['smoothed'] >= info.run_threshold]
            run_idx = np.zeros(pos['time'].shape, dtype=bool)
            for idx in t_run:
                run_idx |= (pos['time'] == idx)

            run_pos = dict()
            run_pos['x'] = pos['x'][run_idx]
            run_pos['y'] = pos['y'][run_idx]
            run_pos['time'] = pos['time'][run_idx]

            t_start = info.task_times['phase3'][0]
            t_stop = info.task_times['phase3'][1]

            t_start_idx = vdm.find_nearest_idx(run_pos['time'], t_start)
            t_stop_idx = vdm.find_nearest_idx(run_pos['time'], t_stop)

            sliced_pos = dict()
            sliced_pos['x'] = run_pos['x'][t_start_idx:t_stop_idx]
            sliced_pos['y'] = run_pos['y'][t_start_idx:t_stop_idx]
            sliced_pos['time'] = run_pos['time'][t_start_idx:t_stop_idx]

            sliced_spikes = dict()
            sliced_spikes['time'] = vdm.time_slice(spikes['time'], t_start, t_stop)
            sliced_spikes['label'] = spikes['label']

            tuning_curves = tuning_curve_2d(sliced_spikes, sliced_pos, xedges, yedges, gaussian_sigma=0.5)

            with open(pickled_tc, 'wb') as fileobj:
                pickle.dump(tuning_curves, fileobj)

        import matplotlib.pyplot as plt
        pos = get_pos(info.pos_mat, info.pxl_to_cm)
        binsize = 3
        xedges = np.arange(pos['x'].min(), pos['x'].max() + binsize, binsize)
        yedges = np.arange(pos['y'].min(), pos['y'].max() + binsize, binsize)
        xx, yy = np.meshgrid(xedges, yedges)
        for tuning_curve in tuning_curves[0:3]:
            pp = plt.pcolormesh(xx, yy, tuning_curve, cmap='YlGn')
            plt.colorbar(pp)
            plt.axis('off')
            plt.show()


else:
    for info in infos:
        print(info.session_id)
        pos = get_pos(info.pos_mat, info.pxl_to_cm)

        tc = get_tc(info, pos, pickle_filepath)

        sort_idx = dict()
        odd_firing_idx = dict()
        sorted_tc = dict(u=[], shortcut=[], novel=[])

        for key in tc:
            sort_idx[key] = vdm.get_sort_idx(tc[key])
            odd_firing_idx[key] = get_odd_firing_idx(tc[key])

            for idx in sort_idx[key]:
                if idx not in odd_firing_idx[key]:
                    sorted_tc[key].append(tc[key][idx])

            filename = info.session_id + '-sorted_tc-' + key + '.png'
            savepath = os.path.join(output_filepath, filename)
            plot_sorted_tc(sorted_tc[key], savepath)

            # for neuron_tc in sorted_tc[key]:
            #     plt.plot(neuron_tc)
            # plt.show()
