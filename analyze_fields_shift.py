import matplotlib.pyplot as plt
import numpy as np
import scipy
import os
import nept

from loading_data import get_data
from analyze_tuning_curves import get_tuning_curves

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, "plots", "fields_shift")


def get_neurons(position, spikes, xedges, yedges, phase):

    sliced_position = position.time_slice(info.task_times[phase].start, info.task_times[phase].stop)
    sliced_spikes = [spiketrain.time_slice(info.task_times[phase].start, info.task_times[phase].stop)
                     for spiketrain in spikes]

    neurons = get_tuning_curves(info,
                                sliced_position,
                                sliced_spikes,
                                xedges,
                                yedges,
                                speed_limit=0.4,
                                phase_id=phase,
                                min_n_spikes=None,
                                trial_times=None,
                                trial_number=None,
                                cache=False
                                )

    return neurons


def tuning_curve_shift(neurons1, neurons2):
    """Computes the difference between tuning curves from the same session

    Note that directionality matters! Positive values will result from shifts of
    the tuning curves toward that location for neurons2 and negative values away from that
    location for neurons2.

    Parameters
    ==========
    neurons1: nept.Neurons
    neurons2: nept.Neurons

    Returns
    =======
    tuning_curves_shift: np.array
    tuning_curves_shift_avg: np.array

    """

    if neurons1.tuning_shape != neurons2.tuning_shape:
        raise AssertionError("tuning curves must have the same shape")

    if neurons1.n_neurons != neurons2.n_neurons:
        raise AssertionError("neuron objects must have the same number of tuning curves")

    tuning_curves_shift = np.zeros(neurons1.tuning_shape)
    for idx in range(neurons1.n_neurons):
        tuning_curves_shift += neurons2.tuning_curves[idx] - neurons1.tuning_curves[idx]

    return tuning_curves_shift, tuning_curves_shift / neurons1.n_neurons


def plot_fields_shift(info):

    events, position, spikes, lfp, lfp_theta = get_data(info)
    xedges, yedges = nept.get_xyedges(position)

    neurons_phase1 = get_neurons(position, spikes, xedges, yedges, "phase1")
    neurons_phase2 = get_neurons(position, spikes, xedges, yedges, "phase2")
    neurons_phase3 = get_neurons(position, spikes, xedges, yedges, "phase3")

    tuning_curves_shift12, tuning_curves_shift_avg12 = tuning_curve_shift(neurons_phase1, neurons_phase2)
    tuning_curves_shift23, tuning_curves_shift_avg23 = tuning_curve_shift(neurons_phase2, neurons_phase3)
    tuning_curves_shift13, tuning_curves_shift_avg13 = tuning_curve_shift(neurons_phase1, neurons_phase3)

    xx, yy = np.meshgrid(xedges, yedges)

    pp = plt.pcolormesh(xx, yy, tuning_curves_shift12, cmap='gray_r')
    plt.colorbar(pp)
    plt.axis('off')
    filename = os.path.join(output_filepath, info.session_id + "_tuning_curve_shift12.png")
    plt.savefig(filename)
    plt.close()

    pp = plt.pcolormesh(xx, yy, tuning_curves_shift23, cmap='gray_r')
    plt.colorbar(pp)
    plt.axis('off')
    filename = os.path.join(output_filepath, info.session_id + "_tuning_curve_shift23.png")
    plt.savefig(filename)
    plt.close()

    pp = plt.pcolormesh(xx, yy, tuning_curves_shift13, cmap='gray_r')
    plt.colorbar(pp)
    plt.axis('off')
    filename = os.path.join(output_filepath, info.session_id + "_tuning_curve_shift13.png")
    plt.savefig(filename)
    plt.close()


if __name__ == "__main__":
    from run import spike_sorted_infos, info
    infos = spike_sorted_infos
    # infos = [info.r066d5]

    for info in infos:
        print(info.session_id)
        plot_fields_shift(info)
