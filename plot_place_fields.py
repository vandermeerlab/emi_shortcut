import os
import numpy as np
import matplotlib.pyplot as plt
import pickle
import nept

from loading_data import get_data


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'fields')


from run import spike_sorted_infos
infos = spike_sorted_infos

for info in infos:
    print('place_fields:', info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = nept.get_xyedges(position)

    speed = position.speed(t_smooth=0.8)
    run_idx = np.squeeze(speed.data) >= 0.1
    run_pos = position[run_idx]

    t_start = info.task_times['phase3'].start
    t_stop = info.task_times['phase3'].stop

    sliced_pos = run_pos.time_slice(t_start, t_stop)

    neurons_filename = info.session_id + '_neurons.pkl'
    pickled_neurons = os.path.join(pickle_filepath, neurons_filename)
    if os.path.isfile(pickled_neurons):
        with open(pickled_neurons, 'rb') as fileobj:
            neurons = pickle.load(fileobj)
    else:
        raise ValueError("no neuron file found for", info.session_id)

    sliced_spikes = neurons.time_slice(t_start, t_stop)

    heatmap_filename = info.session_id + '_spike_heatmaps.pkl'
    pickled_spike_heatmaps = os.path.join(pickle_filepath, heatmap_filename)
    if os.path.isfile(pickled_spike_heatmaps):
        with open(pickled_spike_heatmaps, 'rb') as fileobj:
            spike_heatmaps = pickle.load(fileobj)
    else:
        all_neurons = list(range(0, len(spikes)))
        spike_heatmaps = nept.get_heatmaps(all_neurons, spikes, position)
        with open(pickled_spike_heatmaps, 'wb') as fileobj:
            pickle.dump(spike_heatmaps, fileobj)

    fields = nept.find_fields(neurons.tuning_curves)

    fields_single = nept.get_single_field(fields)

    all_tuning_curves = np.zeros(neurons.tuning_shape)
    for i in range(neurons.n_neurons):
        all_tuning_curves += neurons.tuning_curves[i]

    filename = info.session_id + '-fields.png'
    savepath = os.path.join(output_filepath, filename)

    xx, yy = np.meshgrid(xedges, yedges)

    pp = plt.pcolormesh(xx, yy, all_tuning_curves, cmap='pink_r')
    plt.colorbar(pp)
    plt.axis('off')
    plt.savefig(savepath, transparent=True)
