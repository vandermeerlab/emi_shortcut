import os
import numpy as np
import pickle
from collections import OrderedDict
from shapely.geometry import LineString

from utils_plotting import plot_decoded_compare, plot_decoded_session_errors

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


def load_decoded(info, experiment_times, pickle_filepath, f_combine, shuffled=False):
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

        decode_together[experiment_time] = f_combine(info, decoded, experiment_time)

    return decode_together


def get_zone_proportion(info, decoded, experiment_time):
    """Computes the proportion of n_samples in each zone

    Parameters
    ----------
    info: module
    decoded: nept.Position

    Returns: dict

    """
    # print('Working on', info.session_id)

    if experiment_time not in ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']:
        raise ValueError("experiment time is not recognized as a shortcut experiment time.")

    n_total = 0
    for zone in ['u', 'shortcut', 'novel']:
        n_total += decoded['zones'][zone].n_samples
    n_total = np.maximum(n_total, 1.0)

    decoded_proportions = dict()
    for zone in ['u', 'shortcut', 'novel']:
        decoded_proportions[zone] = decoded['zones'][zone].n_samples / n_total

    return decoded_proportions


def get_proportion_normalized(info, decoded, experiment_time):
    """Finds decoded proportions normalized by track length

    Parameters
    ----------
    info: module
    decoded: nept.Position
    experiment_time: str

    Returns
    -------
    normalized_proportions: dict
        With u, shortcut, novel as keys

    """
    # print('Working on', info.session_id)

    if experiment_time not in ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']:
        raise ValueError("experiment time is not recognized as a shortcut experiment time.")

    length = dict()
    length['u'] = LineString(info.u_trajectory).length
    length['shortcut'] = LineString(info.shortcut_trajectory).length
    length['novel'] = LineString(info.novel_trajectory).length

    n_total = 0
    for zone in ['u', 'shortcut', 'novel']:
        n_total += decoded['zones'][zone].n_samples / length[zone]
    n_total = np.maximum(n_total, 1.0)

    proportions_normalized = dict()
    for zone in ['u', 'shortcut', 'novel']:
        proportions_normalized[zone] = (decoded['zones'][zone].n_samples / length[zone]) / n_total

    return proportions_normalized


def get_errors(info, decoded, experiment_time):
    """Computes the error of decoded position compared to actual position

    Parameters
    ----------
    info: module
    decoded: nept.Position

    Returns: dict

    """
    # print('Working on', info.session_id)

    decoded_error = dict()
    for key in decoded['actual'].keys():
        if experiment_time in ['phase1', 'phase2', 'phase3']:
            decoded_error[key] = decoded['zones'][key].distance(decoded['actual'][key])
        else:
            decoded_error[key] = 0

    return decoded_error


def get_session_errors(info, experiment_time, shuffled):
    """Loads the error of decoded position compared to actual position

    Parameters
    ----------
    info: module
    experiment_time: str
    shuffled: boolean

    Returns
    -------
    errors: np.array

    """
    if experiment_time in ['phase1', 'phase2', 'phase3']:
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

        return decoded['errors']
    else:
        return np.array([])


def get_combined(infos, experiment_times):
    sessions = []

    for info in infos:
        combined = OrderedDict()

        for experiment_time in experiment_times:
            combined[experiment_time] = dict()

            filename = '_decode-' + experiment_time + '.pkl'
            decode_filename = info.session_id + filename
            pickled_decoded = os.path.join(pickle_filepath, decode_filename)

            with open(pickled_decoded, 'rb') as fileobj:
                decoded = pickle.load(fileobj)

            for key in ['u', 'shortcut', 'novel']:
                combined[experiment_time][key] = decoded['zones'][key]

        sessions.append(combined)

    return sessions


if __name__ == "__main__":
    from run import spike_sorted_infos, days123_infos, days456_infos, error_infos, info

    # infos = spike_sorted_infos
    # session = 'combined'

    infos = [info.r066d4]
    session = 'r066d4'

    if 1:
        experiment_times = ['pauseA', 'pauseB']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_decode_pauses.png')
        plot_decoded_compare(decodes, savepath=filename)

        experiment_times = ['phase1', 'phase2', 'phase3']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_decode_phases.png')
        plot_decoded_compare(decodes, savepath=filename)

        experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_decode_all.png')
        plot_decoded_compare(decodes, savepath=filename)

        experiment_times = ['prerecord', 'postrecord']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_decode_prepost.png')
        plot_decoded_compare(decodes, savepath=filename)

    # plot errors
    if 1:
        experiment_times = ['phase1', 'phase2', 'phase3']

        for experiment_time in experiment_times:
            errors = []
            errors_shuffled = []
            n_sessions = 0
            for this_info in infos:
                errors.extend(get_session_errors(this_info, experiment_time, shuffled=False))
                errors_shuffled.extend(get_session_errors(this_info, experiment_time, shuffled=True))
                n_sessions += 1

            filename = os.path.join(output_filepath, session + '_errors_' + experiment_time + '.png')
            plot_decoded_session_errors(errors, errors_shuffled, n_sessions, savepath=filename)

    # Plot by track length
    if 1:
        experiment_times = ['phase1', 'phase2', 'phase3']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_track-length_phases.png')
        plot_decoded_compare(decodes, ylabel='Proportion relative to track length', savepath=filename)

        experiment_times = ['pauseA', 'pauseB']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_track-length_pauses.png')
        plot_decoded_compare(decodes, ylabel='Proportion relative to track length', savepath=filename)

        experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_track-length_all.png')
        plot_decoded_compare(decodes, ylabel='Proportion relative to track length', savepath=filename)

        experiment_times = ['prerecord', 'postrecord']
        decodes = []
        for this_info in infos:
            decodes.append(load_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))
        filename = os.path.join(output_filepath, session + '_track-length_prepost.png')
        plot_decoded_compare(decodes, ylabel='Proportion relative to track length', savepath=filename)
