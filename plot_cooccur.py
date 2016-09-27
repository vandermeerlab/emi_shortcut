import os
import numpy as np
import pickle

import vdmlab as vdm

from load_data import get_pos, get_spikes, get_lfp
from analyze_fields import get_unique_fields, categorize_fields
from analyze_maze import find_zones
from analyze_cooccur import analyze
from analyze_plotting import plot_cooccur, plot_cooccur_combined, plot_cooccur_weighted_pauses

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')


def combine_cooccur_weighted(cooccurs):
    """Combines probabilities from multiple sessions, weighted by number of sharp-wave ripple events.

    Parameters
    ----------
    all_probs: list of dicts
        With u, shortcut, novel as keys,
        each a dict with expected, observed, active, shuffle, zscore as keys.
    n_epochs: list of ints

    Returns
    -------
    combined_weighted: list

    """
    combined_weighted = dict(u=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                             shortcut=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                             novel=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]))

    for trajectory in combined_weighted:
        for key in combined_weighted[trajectory]:
            for probs, n_epoch in zip(cooccurs['probs'], cooccurs['n_epochs']):
                if np.sum(probs[trajectory][key]) > 0:
                    combined_weighted[trajectory][key].append(np.nanmean(probs[trajectory][key]) * n_epoch)
                else:
                    combined_weighted[trajectory][key].append(0.0)

    return combined_weighted


def combine_cooccur(cooccurs):
    """Combines probabilities from multiple sessions.

    Parameters
    ----------
    all_probs: list of dicts
        With u, shortcut, novel as keys,
        each a dict with expected, observed, active, shuffle, zscore as keys.
    n_epochs: list of ints

    Returns
    -------
    combined: list

    """
    combined = dict(u=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                    shortcut=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]),
                    novel=dict(expected=[], observed=[], active=[], shuffle=[], zscore=[]))

    for trajectory in combined:
        for key in combined[trajectory]:
            for probs in cooccurs['probs']:
                if np.sum(probs[trajectory][key]) > 0:
                    combined[trajectory][key].extend(probs[trajectory][key])
                else:
                    combined[trajectory][key].append(0.0)
    return combined


def plot(infos, all_tracks_tc=False):
    cooccurs_a = dict(probs=[], n_epochs=[])
    cooccurs_b = dict(probs=[], n_epochs=[])
    experiment_time = 'pauseA'
    print('getting co-occurrence', experiment_time)
    for info in infos:
        if all_tracks_tc:
            cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '_all-tracks.pkl'
        else:
            cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '.pkl'
        pickled_cooccur = os.path.join(pickle_filepath, cooccur_filename)
        with open(pickled_cooccur, 'rb') as fileobj:
            cooccur = pickle.load(fileobj)

        cooccurs_a['probs'].append(cooccur['probs'])
        cooccurs_a['n_epochs'].append(cooccur['n_epochs'])

    combined_a = combine_cooccur(cooccurs_a)
    combined_weighted_a = combine_cooccur_weighted(cooccurs_a)

    if all_tracks_tc:
        filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '_all-tracks.pdf'
    else:
        filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '.pdf'
    savepath_weighted = os.path.join(output_filepath, filename_weighted)
    plot_cooccur_combined(combined_weighted_a, int(np.sum(cooccurs_a['n_epochs'])), savepath_weighted)

    filename = 'combined_cooccur-' + experiment_time + '.png'
    savepath = os.path.join(output_filepath, filename)
    plot_cooccur(combined_a, savepath)

    experiment_time = 'pauseB'
    print('getting co-occurrence', experiment_time)
    for info in infos:
        if all_tracks_tc:
            cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '_all-tracks.pkl'
        else:
            cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '.pkl'
        pickled_cooccur = os.path.join(pickle_filepath, cooccur_filename)
        with open(pickled_cooccur, 'rb') as fileobj:
            cooccur = pickle.load(fileobj)

        cooccurs_b['probs'].append(cooccur['probs'])
        cooccurs_b['n_epochs'].append(cooccur['n_epochs'])

    combined_b = combine_cooccur(cooccurs_b)
    combined_weighted_b = combine_cooccur_weighted(cooccurs_b)

    if all_tracks_tc:
        filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '_all-tracks.pdf'
    else:
        filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '.pdf'
    savepath_weighted = os.path.join(output_filepath, filename_weighted)
    plot_cooccur_combined(combined_weighted_b, int(np.sum(cooccurs_b['n_epochs'])), savepath_weighted)

    filename = 'combined_cooccur-' + experiment_time + '.png'
    savepath = os.path.join(output_filepath, filename)
    plot_cooccur(combined_b, savepath)

    filename = 'pauses-combined_cooccur.png'
    savepath = os.path.join(output_filepath, filename)
    plot_cooccur_weighted_pauses(combined_weighted_a, cooccurs_a['n_epochs'],
                                 combined_weighted_b, cooccurs_b['n_epochs'],
                                 ['pauseA', 'pauseB'], prob='zscore', ylabel='SWR co-activation z-scored',
                                 savepath=savepath)


def get_outputs_combined_weighted(infos):
    outputs = [os.path.join(output_filepath, 'pauses-combined_cooccur.png')]
    return outputs


if __name__ == "__main__":
    from run import spike_sorted_infos
    infos = spike_sorted_infos

    all_tracks_tc = True
    if all_tracks_tc:
        plot(infos, all_tracks_tc)
    else:
        plot(infos)
