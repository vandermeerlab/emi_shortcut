import os
import numpy as np
import pickle
from collections import OrderedDict
from shapely.geometry import LineString

from utils_plotting import plot_decoded_errors, plot_decoded_compare

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'decode')


def get_zone_proportion(decoded, experiment_time):
    """Computes the proportion of n_samples in each zone

    Parameters
    ----------
    decoded: nept.Position

    Returns: dict

    """
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


def get_decoded(info, experiment_times, pickle_filepath, f_combine, shuffled=False, min_samples=15):
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
    decoded: nept.Position

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


def compare_rates(combined_zones, jump=0.1):
    """Compare position normalized by time spent in zone

    Parameters
    ----------
    combined_zones: list of OrderedDict of dict of lists
        With experiment_time as keys and inner dict
        has u, shortcut, novel as keys.
    jump: float
        Any duration above this amount will not be included.

    Returns
    -------
    by_linger : dict
        With u, shortcut, novel as keys.

    """
    by_linger = []

    for session in combined_zones:
        normalized = OrderedDict()
        for experiment_time in combined_zones[0].keys():
            normalized[experiment_time] = dict()

        for experiment_time in session.keys():
            for trajectory in session[experiment_time].keys():
                linger = np.diff(session[experiment_time][trajectory].time)
                linger = np.sum(linger[linger < jump])
                normalized[experiment_time][trajectory] = session[experiment_time][trajectory].n_samples / linger

        by_linger.append(normalized)

    return by_linger


def compare_lengths(infos, combined_zones, timebin=0.025):
    """Compare position normalized by time spent in zone.

    Parameters
    ----------
    infos: list of modules
    combined_zones: list of OrderedDict of dict of lists
        With experiment_time as keys and inner dict
        has u, shortcut, novel as keys.

    Returns
    -------
    by_track_length : list
        Of OrderedDict with experiment_times as keys,
        each a dict with u, shortcut, novel as keys.

    """
    lengths = dict(u=[], shortcut=[], novel=[])
    for info in infos:
        lengths['u'].append(LineString(info.u_trajectory).length)
        lengths['shortcut'].append(LineString(info.shortcut_trajectory).length)
        lengths['novel'].append(LineString(info.novel_trajectory).length)

    by_track_length = []

    for i, session in enumerate(combined_zones):
        normalized = OrderedDict()
        for exp in combined_zones[0].keys():
            normalized[exp] = dict()

        for exp in session.keys():
            for trajectory in session[exp].keys():
                # normalized[exp][trajectory] = (session[exp][trajectory].n_samples * timebin) / lengths[trajectory][i]
                normalized[exp][trajectory] = (session[exp][trajectory].n_samples) / lengths[trajectory][i]

        by_track_length.append(normalized)

    return by_track_length


def get_proportions(norm):
    """Computes the proportion of normalized decoded positions

    Parameters
    ----------
    norm : list
        Of OrderedDict with experiment_times as keys,
        each a dict with u, shortcut, novel as keys.

    Returns
    -------
    proportion : list
        Of OrderedDict with experiment_times as keys,
        each a dict with u, shortcut, novel as keys.

    """

    proportion = []

    for i, session in enumerate(norm):
        session_proportion = OrderedDict()
        n_total = OrderedDict()

        for exp in norm[0].keys():
            session_proportion[exp] = dict()
            n_total[exp] = dict()

        for exp in session.keys():
            n_total[exp] = 0
            for trajectory in session[exp].keys():
                n_total[exp] += norm[i][exp][trajectory]

        for exp in session.keys():
            for trajectory in session[exp].keys():
                n_total[exp] = np.maximum(n_total[exp], 1.0)
                session_proportion[exp][trajectory] = norm[i][exp][trajectory] / n_total[exp]

        proportion.append(session_proportion)

    return proportion


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

    infos = spike_sorted_infos
    session = 'combined'

    # infos = [info.r066d3]
    # session = 'r066d3'

    if 1:
        experiment_times = ['pauseA', 'pauseB']

        decodes = []

        for this_info in infos:
            decodes.append(get_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, session + '_decode_pauses.png')
        plot_decoded_compare(decodes, savepath=filename)


        experiment_times = ['phase1', 'phase2', 'phase3']

        decodes = []

        for this_info in infos:
            decodes.append(get_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, session + '_decode_phases.png')
        plot_decoded_compare(decodes, savepath=filename)

        experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']

        decodes = []

        for this_info in infos:
            decodes.append(get_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, session + '_decode_all.png')
        plot_decoded_compare(decodes, savepath=filename)

        experiment_times = ['prerecord', 'postrecord']

        decodes = []

        for this_info in infos:
            decodes.append(get_decoded(this_info, experiment_times, pickle_filepath, get_zone_proportion))

        filename = os.path.join(output_filepath, session + '_decode_prepost.png')
        plot_decoded_compare(decodes, savepath=filename)

    # plot errors
    if 0:
        experiment_times = ['phase1', 'phase2', 'phase3']

        errors = []
        errors_shuffled = []

        for this_info in infos:
            errors.append(get_decoded(this_info, experiment_times, pickle_filepath, get_errors))
            errors_shuffled.append(get_decoded(this_info, experiment_times, pickle_filepath, get_errors, shuffled=True))

        combine_error = combine_errors(errors)
        combine_error_shuffled = combine_errors(errors_shuffled)
        filename = os.path.join(output_filepath, 'errors_phase1.png')
        plot_decoded_errors(combine_error, combine_error_shuffled, experiment_time='phase1', savepath=filename)
        filename = os.path.join(output_filepath, 'errors_phase2.png')
        plot_decoded_errors(combine_error, combine_error_shuffled, experiment_time='phase2', savepath=filename)
        filename = os.path.join(output_filepath, 'errors_phase3.png')
        plot_decoded_errors(combine_error, combine_error_shuffled, experiment_time='phase3', savepath=filename)

    # Plot by time spent
    if 0:
        experiment_times = ['phase1', 'phase2', 'phase3']
        sessions = get_combined(infos, experiment_times)
        norm_time = compare_rates(sessions)
        filename = os.path.join(output_filepath, 'rate_phases.png')
        plot_decoded_compare(norm_time, ylabel='Total firing rate', savepath=filename)

    # Plot by track length
    if 0:
        experiment_times = ['phase1', 'phase2', 'phase3']
        sessions = get_combined(infos, experiment_times)
        norm_length = compare_lengths(infos, sessions)
        proportion = get_proportions(norm_length)
        filename = os.path.join(output_filepath, session + '_track-length_phases.png')
        plot_decoded_compare(proportion, ylabel='Proportion relative to track length', savepath=filename)

        experiment_times = ['pauseA', 'pauseB']
        sessions = get_combined(infos, experiment_times)
        norm_length = compare_lengths(infos, sessions)
        proportion = get_proportions(norm_length)
        filename = os.path.join(output_filepath, session + '_track-length_pauses.png')
        plot_decoded_compare(proportion, ylabel='Proportion relative to track length', savepath=filename)

        experiment_times = ['prerecord', 'phase1', 'pauseA', 'phase2', 'pauseB', 'phase3', 'postrecord']
        sessions = get_combined(infos, experiment_times)
        norm_length = compare_lengths(infos, sessions)
        proportion = get_proportions(norm_length)
        filename = os.path.join(output_filepath, session + '_track-length_all.png')
        plot_decoded_compare(proportion, ylabel='Proportion relative to track length', savepath=filename)

        experiment_times = ['prerecord', 'postrecord']
        sessions = get_combined(infos, experiment_times)
        norm_length = compare_lengths(infos, sessions)
        proportion = get_proportions(norm_length)
        filename = os.path.join(output_filepath, session + '_track-length_prepost.png')
        plot_decoded_compare(proportion, ylabel='Proportion relative to track length', savepath=filename)
