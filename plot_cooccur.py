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

# filename = 'testing_cooccur-' + experiment_time + '.png'
# savepath = os.path.join(output_filepath, filename)
# plot_cooccur(probs, savepath=None)


if __name__ == "__main__":
    from run import spike_sorted_infos
    infos = spike_sorted_infos

    if 1:
        cooccurs = dict(probs=[], n_epochs=[])
        experiment_times = ['pauseA', 'pauseB']
        for experiment_time in experiment_times:
            for info in infos:
                tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
                pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
                with open(pickled_tuning_curve, 'rb') as fileobj:
                    tuning_curve = pickle.load(fileobj)

                cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '.pkl'
                pickled_cooccur = os.path.join(pickle_filepath, cooccur_filename)
                with open(pickled_cooccur, 'rb') as fileobj:
                    cooccur = pickle.load(fileobj)

                cooccurs['probs'].append(cooccur['probs'])
                cooccurs['n_epochs'].append(cooccur['n_epoch'])

            combined = combine_cooccur(cooccurs)
            combined_weighted = combine_cooccur_weighted(cooccurs)

            filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '.png'
            savepath_weighted = os.path.join(output_filepath, filename_weighted)
            plot_cooccur_combined(combined_weighted, int(np.sum(cooccurs['n_epoch'])), savepath_weighted)

            filename = 'combined_cooccur-' + experiment_time + '.png'
            savepath = os.path.join(output_filepath, filename)
            plot_cooccur(combined, savepath)


# Plot two phase's probs together in the same plot
# if 0:
#     z_thresh = 7.0
#     experiment_times = ['pauseA', 'pauseB']
#     all_probs_a, n_epochs_a = get_cooccur(infos, experiment_times[0], z_thresh=z_thresh)
#     combined_weighted_a = combine_cooccur_weighted(all_probs_a, n_epochs_a)
#
#     all_probs_b, n_epochs_b = get_cooccur(infos, experiment_times[1], z_thresh=z_thresh)
#     combined_weighted_b = combine_cooccur_weighted(all_probs_b, n_epochs_b)
#
#     filename = 'pauses-combined_cooccur_z7.png'
#     savepath = os.path.join(output_filepath, filename)
#     plot_cooccur_weighted_pauses(combined_weighted_a, n_epochs_a, combined_weighted_b, n_epochs_b, experiment_times,
#                         prob='zscore', ylabel='SWR co-activation z-scored', savepath=savepath)
