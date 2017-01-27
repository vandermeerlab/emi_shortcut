import os
import pickle
from collections import OrderedDict

from analyze_decode import compare_rates, compare_lengths, combine_decode
from utils_plotting import plot_decoded_errors, plot_decoded_compare

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


def normalized_time_spent(combined_decoded, n_sessions, lengths, filenames):
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

    savepath = os.path.join(output_filepath, filenames[0])
    y_label = 'Points normalized by time spent'
    plot_decoded(decoded_linger, y_label=y_label, savepath=savepath)

    savepath = os.path.join(output_filepath, filenames[1])
    y_label = 'Points normalized by track length'
    plot_decoded(decoded_length, y_label=y_label, savepath=savepath)


def get_zone_proportion(decoded, experiment_time):
    """Computes the proportion of n_samples in each zone

    Parameters
    ----------
    decoded: vdmlab.Position

    Returns: dict

    """
    if experiment_time not in ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']:
        raise ValueError("experiment time is not recognized as a shortcut experiment time.")

    zones = decoded['zones'].keys()
    n_total = decoded['decoded'].n_samples

    decoded_proportions = dict()
    for zone in zones:
        decoded_proportions[zone] = decoded['zones'][zone].n_samples / n_total

    return decoded_proportions


def get_decoded(info, experiment_times, pickle_filepath, f_combine, shuffled=False):
    """Combines decoded outputs

    Parameters
    ----------
    info: module
    experiment_times: list of str
    pickle_filepath: str
    f_combine: function
        Either get_zone_proportion or get_errors

    Returns
    -------
    decode_together: OrderedDict
        With experiment_time as keys, each a dict
        with u, shortcut, novel, other as keys.

    """

    decode_together = OrderedDict()

    for experiment_time in experiment_times:
        if shuffled:
            filename = '_decode-shuffled-' + experiment_time + '.pkl'
        else:
            filename = '_decode-' + experiment_time + '.pkl'
        decode_filename = info.session_id + filename
        pickled_decoded = os.path.join(pickle_filepath, decode_filename)

        if os.path.isfile(pickled_decoded):
            with open(pickled_decoded, 'rb') as fileobj:
                decoded = pickle.load(fileobj)
        else:
            raise ValueError("pickled decoded not found for " + info.session_id)

        decode_together[experiment_time] = f_combine(decoded, experiment_time)

    return decode_together


def get_errors(decoded, experiment_time):
    """Computes the error of decoded position compared to actual position

    Parameters
    ----------
    decoded: vdmlab.Position

    Returns: dict

    """
    decoded_error = dict()
    for key in decoded['actual'].keys():
        if experiment_time in ['phase1', 'phase2', 'phase3']:
            decoded_error[key] = decoded['zones'][key].distance(decoded['actual'][key])
        else:
            decoded_error[key] = 0

    return decoded_error


def combine_errors(errors):
    """Combines errors from  multiple sessions

    Parameters
    ----------
    errors: list of OrderedDicts
        With experiment times as keys, each a dict
        with u, shortcut, novel as keys.

    Returns
    -------
    combine_errors: OrderedDict
        With experiment times as keys, each a dict
        with u, shortcut, novel, together as keys.

    """
    combine_errors = OrderedDict()

    for key in errors[0].keys():
        combine_errors[key] = dict(u=[], shortcut=[], novel=[], together=[])
        for error in errors:
            for trajectory in error[key].keys():
                combine_errors[key][trajectory].extend(error[key][trajectory])
                combine_errors[key]['together'].extend(error[key][trajectory])

    return combine_errors


def get_summary(decoded, times):
    decode = dict(u=[], shortcut=[], novel=[])
    for key in decode:
        for session in range(len(times)):
            decode[key].append(len(decoded[key][session].time)/times[session])
    return decode


def plot_normalized(infos, tuning_curves, all_tracks_tc=False):
    # Plot decoding normalized by time spent
    experiment_time = 'phase3'
    print('getting decoded', experiment_time)
    decoded_phase3 = combine_decode(infos, '_decode-' + experiment_time + '.pkl', experiment_time=experiment_time,
                                    shuffle_id=False, tuning_curves=tuning_curves)
    print('normalizing ...')
    n_sessions = len(infos)
    if all_tracks_tc:
        filenames = ['combined-time-norm_tracks_decoded_all-tracks.png',
                     'combined-length-norm_tracks_decoded_all-tracks.png']
    else:
        filenames = ['combined-time-norm_tracks_decoded.png', 'combined-length-norm_tracks_decoded.png']
    normalized_time_spent(decoded_phase3['combined_decoded'], n_sessions, decoded_phase3['combined_lengths'],
                          filenames)


if __name__ == "__main__":
    from run import spike_sorted_infos, days123_infos, days456_infos, error_infos
    infos = spike_sorted_infos

    if 0:
        experiment_times = ['pauseA', 'pauseB']

        decodes = []

        for info in infos:
            decodes.append(get_decoded(info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, 'decode_pauses.png')
        plot_decoded_compare(decodes, savepath=filename)


        experiment_times = ['phase1', 'phase2', 'phase3']

        decodes = []

        for info in infos:
            decodes.append(get_decoded(info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, 'decode_phases.png')
        plot_decoded_compare(decodes, savepath=filename)

        experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']

        decodes = []

        for info in infos:
            decodes.append(get_decoded(info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, 'decode_all.png')
        plot_decoded_compare(decodes, savepath=filename)


        experiment_times = ['prerecord', 'postrecord']

        decodes = []

        for info in infos:
            decodes.append(get_decoded(info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, 'decode_prepost.png')
        plot_decoded_compare(decodes, savepath=filename)

    # plot errors
    if 0:
        experiment_times = ['phase1', 'phase2', 'phase3']

        errors = []
        errors_shuffled = []

        for info in infos:
            errors.append(get_decoded(info, experiment_times, pickle_filepath, get_errors))
            errors_shuffled.append(get_decoded(info, experiment_times, pickle_filepath, get_errors, shuffled=True))

        combine_error = combine_errors(errors)
        combine_error_shuffled = combine_errors(errors_shuffled)
        filename = os.path.join(output_filepath, 'errors_phase1.png')
        plot_decoded_errors(combine_error, combine_error_shuffled, experiment_time='phase1', savepath=filename)
        filename = os.path.join(output_filepath, 'errors_phase2.png')
        plot_decoded_errors(combine_error, combine_error_shuffled, experiment_time='phase2', savepath=filename)
        filename = os.path.join(output_filepath, 'errors_phase3.png')
        plot_decoded_errors(combine_error, combine_error_shuffled, experiment_time='phase3', savepath=filename)
