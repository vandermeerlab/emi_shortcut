import os
import numpy as np
import pickle

from analyze_decode import analyze, compare_rates, compare_lengths
from analyze_plotting import (plot_decoded, plot_decoded_pause, plot_decoded_errors,
                                plot_compare_decoded_pauses)

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


def normalized_time_spent(combined_decoded, n_sessions, lengths):
    decoded_linger = dict(u=[], shortcut=[], novel=[])
    decoded_length = dict(u=[], shortcut=[], novel=[])
    for val in range(n_sessions):
        decode = dict()
        length = dict()
        for key in decoded_linger:
            decode[key] = combined_decoded[key][val]
            length[key] = lengths[key][val]
        norm_decoded = compare_rates(decode)
        len_decoded = compare_lengths(decode, length)
        for key in decoded_linger:
            decoded_linger[key].append(norm_decoded[key])
            decoded_length[key].append(len_decoded[key])

    filename = 'combined-time-norm_tracks_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    y_label = 'Points normalized by time spent'
    plot_decoded(decoded_linger, y_label=y_label, max_y=None, savepath=savepath)

    filename = 'combined-length-norm_tracks_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    y_label = 'Points normalized by track length'
    plot_decoded(decoded_length, y_label=y_label, max_y=None, savepath=savepath)


def plot_errors(infos, tuning_curves):
    # Plot decoding errors during track times
    combined_decoded, combined_errors, total_times, lengths = analyze(infos, tuning_curves, shuffle_id=False)
    print('Mean decoded errors:', np.mean(combined_errors))
    shuffled_decoded, shuffled_errors, shuffled_times, shuffled_lengths = analyze(infos, tuning_curves, shuffle_id=True)
    print('Mean shuffled errors:', np.mean(combined_errors))
    filename = 'combined-errors_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_errors(combined_errors, shuffled_errors, fliersize=3, savepath=savepath)


def plot_pauses(infos, tuning_curves):
    # Plot proportion of pauseA and pauseB spent in each trajectory
    experiment_time = 'pauseA'
    decoded_pausea, errors_pausea, times_pausea, lengths_pausea = analyze(infos, tuning_curves, experiment_time)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_pausea, times_pausea, savepath=savepath)

    experiment_time = 'pauseB'
    decoded_pauseb, errors_pauseb, times_pauseb, lengths_pauseb = analyze(infos, tuning_curves, experiment_time)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_pauseb, times_pauseb, savepath=savepath)

    filename = 'combined-pauses_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_compare_decoded_pauses(decoded_pausea, times_pausea, decoded_pauseb, times_pauseb, ['Pause A', 'Pause B'],
                                savepath=savepath)


def plot_phases(infos, tuning_curves):
    # Plot proportion of pauseA and pauseB spent in each trajectory
    experiment_time = 'phase2'
    decoded_phase1, errors_phase1, times_phase1, lengths_phase1 = analyze(infos, tuning_curves, experiment_time)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_phase1, times_phase1, savepath=savepath)

    experiment_time = 'phase3'
    decoded_phase3, errors_phase3, times_phase3, lengths_phase3 = analyze(infos, tuning_curves, experiment_time)
    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_phase3, times_phase3, savepath=savepath)

    filename = 'combined-phases_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_compare_decoded_pauses(decoded_phase1, times_phase1, decoded_phase3, times_phase3, ['Phase 2', 'Phase 3'],
                                savepath=savepath)


def plot_normalized(infos, tuning_curves):
    # Plot decoding normalized by time spent
    combined_decoded, combined_errors, total_times, lengths = analyze(infos, tuning_curves)
    n_sessions = len(infos)
    normalized_time_spent(combined_decoded, n_sessions, lengths)


outputs_errors = [os.path.join(output_filepath, 'combined-errors_decoded.png')]

outputs_pauses = [os.path.join(output_filepath, 'combined-pauses_decoded.png')]

outputs_phases = [os.path.join(output_filepath, 'combined-phases_decoded.png')]

outputs_normalized = [os.path.join(output_filepath, 'combined-time-norm_tracks_decoded.png'),
                      os.path.join(output_filepath, 'combined-length-norm_tracks_decoded.png')]


if __name__ == "__main__":
    from run import all_infos, spike_sorted_infos
    infos = spike_sorted_infos

    tuning_curves = []
    for info in infos:
        tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
        pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
        with open(pickled_tuning_curve, 'rb') as fileobj:
            tuning_curves.append(pickle.load(fileobj))

    plot_errors(infos, tuning_curves)
    plot_pauses(infos, tuning_curves)
    plot_phases(infos, tuning_curves)
    plot_normalized(infos, tuning_curves)
