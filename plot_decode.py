import os
import numpy as np
import pickle

from analyze_decode import analyze, compare_rates, compare_lengths, combine_decode
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
    plot_decoded(decoded_linger, y_label=y_label, savepath=savepath)

    filename = 'combined-length-norm_tracks_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    y_label = 'Points normalized by track length'
    plot_decoded(decoded_length, y_label=y_label, savepath=savepath)


def plot_errors(infos, tuning_curves):
    experiment_time = 'tracks'
    print('getting decoded', experiment_time)
    decoded = combine_decode(infos, '_decode-tracks.pkl', experiment_time=experiment_time,
                                        shuffle_id=False, tuning_curves=tuning_curves)

    print('getting decoded', experiment_time, 'shuffled')
    decoded_shuffle = combine_decode(infos, '_decode-tracks-shuffled.pkl', experiment_time='tracks',
                                        shuffle_id=True, tuning_curves=tuning_curves)

    filename = 'combined-errors_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_errors(decoded['combined_errors'], decoded_shuffle['combined_errors'], fliersize=3, savepath=savepath)


def plot_pauses(infos, tuning_curves):
    # Plot proportion of pauseA and pauseB spent in each trajectory
    experiment_time = 'pauseA'
    print('getting decoded', experiment_time)
    decoded_pausea = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                    shuffle_id=False, tuning_curves=tuning_curves)

    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_pausea['combined_decoded'], decoded_pausea['total_times'], savepath=savepath)

    experiment_time = 'pauseB'
    print('getting decoded', experiment_time)
    decoded_pauseb = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                    shuffle_id=False, tuning_curves=tuning_curves)

    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_pauseb['combined_decoded'], decoded_pauseb['total_times'], savepath=savepath)

    filename = 'combined-pauses_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_compare_decoded_pauses(decoded_pausea['combined_decoded'], decoded_pausea['total_times'],
                                decoded_pauseb['combined_decoded'], decoded_pauseb['total_times'],
                                ['Pause A', 'Pause B'], savepath=savepath)


def plot_phases(infos, tuning_curves):
    # Plot proportion of phase2 and phase3 spent in each trajectory
    experiment_time = 'phase2'
    print('getting decoded', experiment_time)
    decoded_phase2 = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                    shuffle_id=False, tuning_curves=tuning_curves)

    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_phase2['combined_decoded'], decoded_phase2['total_times'], savepath=savepath)

    experiment_time = 'phase3'
    print('getting decoded', experiment_time)
    decoded_phase3 = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                    shuffle_id=False, tuning_curves=tuning_curves)

    filename = 'combined-' + experiment_time + '_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_decoded_pause(decoded_phase3['combined_decoded'], decoded_phase3['total_times'], savepath=savepath)

    filename = 'combined-pauses_decoded.png'
    savepath = os.path.join(output_filepath, filename)
    plot_compare_decoded_pauses(decoded_phase2['combined_decoded'], decoded_phase2['total_times'],
                                decoded_phase3['combined_decoded'], decoded_phase3['total_times'],
                                ['Pause A', 'Pause B'], savepath=savepath)


def plot_normalized(infos, tuning_curves):
    # Plot decoding normalized by time spent
    experiment_time = 'phase3'
    print('getting decoded', experiment_time)
    decoded_phase3 = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                    shuffle_id=False, tuning_curves=tuning_curves)
    print('normalizing ...')
    n_sessions = len(infos)
    normalized_time_spent(decoded_phase3['combined_decoded'], n_sessions, decoded_phase3['combined_lengths'])


def get_outputs_errors(infos):
    outputs = []
    for info in infos:
        outputs.append(os.path.join(output_filepath, info.session_id + '_decode-tracks.png'))
        outputs.append(os.path.join(output_filepath, info.session_id + '_decode-tracks-shuffled.png'))
    return outputs


def get_outputs_pauses(infos):
    outputs = []
    for info in infos:
        outputs.append(os.path.join(output_filepath, info.session_id + '_decode-pauseA.png'))
        outputs.append(os.path.join(output_filepath, info.session_id + '_decode-pauseB.png'))
    outputs.append(os.path.join(output_filepath, 'combined-pauses_decoded.png'))
    return outputs


def get_outputs_phases(infos):
    outputs = []
    for info in infos:
        outputs.append(os.path.join(output_filepath, info.session_id + '_decode-phase2.png'))
        outputs.append(os.path.join(output_filepath, info.session_id + '_decode-phase3.png'))
    outputs.append(os.path.join(output_filepath, 'combined-phases_decoded.png'))
    return outputs


def get_outputs_normalized(infos):
    outputs = [os.path.join(output_filepath, 'combined-time-norm_tracks_decoded.png'),
               os.path.join(output_filepath, 'combined-length-norm_tracks_decoded.png')]
    return outputs


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
