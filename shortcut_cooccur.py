import os
import numpy as np

import vdmlab as vdm

from load_data import get_pos, get_spikes, get_lfp
from field_functions import get_unique_fields, categorize_fields
from maze_functions import find_zones
from plotting_functions import plot_cooccur, plot_cooccur_combined, plot_cooccur_weighted_pauses

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
import info.R063d4_info as r063d4
import info.R063d5_info as r063d5
import info.R063d6_info as r063d6
import info.R066d1_info as r066d1
import info.R066d2_info as r066d2
import info.R066d3_info as r066d3
import info.R066d4_info as r066d4
import info.R066d5_info as r066d5
import info.R067d1_info as r067d1
import info.R067d2_info as r067d2
import info.R067d3_info as r067d3
import info.R067d4_info as r067d4
import info.R067d5_info as r067d5
import info.R068d1_info as r068d1
import info.R068d2_info as r068d2
import info.R068d3_info as r068d3
import info.R068d4_info as r068d4
import info.R068d5_info as r068d5
import info.R068d6_info as r068d6


thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')


def get_cooccur(infos, experiment_time):
    field_thresh = 1.
    power_thresh = 5.
    z_thresh = 3.
    merge_thresh = 0.02
    min_length = 0.01

    n_epochs = []
    all_probs = []

    for info in infos:
        print(info.session_id)

        lfp = get_lfp(info.good_swr[0])
        position = get_pos(info.pos_mat, info.pxl_to_cm)
        spikes = get_spikes(info.spike_mat)

        speed = position.speed(t_smooth=0.5)
        run_idx = np.squeeze(speed.data) >= 0.1
        run_pos = position[run_idx]

        t_start_tc = info.task_times['phase3'].start
        t_stop_tc = info.task_times['phase3'].stop

        tc_pos = run_pos.time_slice(t_start_tc, t_stop_tc)

        tc_spikes = [spiketrain.time_slice(t_start_tc, t_stop_tc) for spiketrain in spikes]

        binsize = 3
        xedges = np.arange(tc_pos.x.min(), tc_pos.x.max() + binsize, binsize)
        yedges = np.arange(tc_pos.y.min(), tc_pos.y.max() + binsize, binsize)

        tuning_curves = vdm.tuning_curve_2d(tc_pos, tc_spikes, xedges, yedges, gaussian_sigma=0.1)

        zones = find_zones(info)

        fields_tunings = categorize_fields(tuning_curves, zones, xedges, yedges, field_thresh=field_thresh)

        keys = ['u', 'shortcut', 'novel']
        unique_fields = dict()
        unique_fields['u'] = get_unique_fields(fields_tunings['u'],
                                               fields_tunings['shortcut'],
                                               fields_tunings['novel'])
        unique_fields['shortcut'] = get_unique_fields(fields_tunings['shortcut'],
                                                      fields_tunings['novel'],
                                                      fields_tunings['u'])
        unique_fields['novel'] = get_unique_fields(fields_tunings['novel'],
                                                   fields_tunings['u'],
                                                   fields_tunings['shortcut'])

        field_spikes = dict(u=[], shortcut=[], novel=[])
        for field in unique_fields.keys():
            for key in unique_fields[field]:
                field_spikes[field].append(spikes[key])

        t_start = info.task_times[experiment_time].start
        t_stop = info.task_times[experiment_time].stop

        sliced_lfp = lfp.time_slice(t_start, t_stop)

        sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

        swrs = vdm.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                      power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

        multi_swrs = vdm.find_multi_in_epochs(sliced_spikes, swrs, min_involved=3)

        n_epochs.append(multi_swrs.n_epochs)

        count_matrix = dict()
        for key in field_spikes:
            count_matrix[key] = vdm.spike_counts(field_spikes[key], multi_swrs)

        tetrode_mask = dict()
        for key in field_spikes:
            tetrode_mask[key] = vdm.get_tetrode_mask(field_spikes[key])

        probs = dict()
        for key in count_matrix:
            probs[key] = vdm.compute_cooccur(count_matrix[key], tetrode_mask[key], num_shuffles=10000)

        all_probs.append(probs)

    return all_probs, n_epochs


def combine_cooccur_weighted(all_probs, n_epochs):
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
            for probs, n_epoch in zip(all_probs, n_epochs):
                if np.sum(probs[trajectory][key]) > 0:
                    combined_weighted[trajectory][key].append(np.nanmean(probs[trajectory][key]) * n_epoch)
                else:
                    combined_weighted[trajectory][key].append(0.0)

    return combined_weighted


def combine_cooccur(all_probs):
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
            for probs in all_probs:
                if np.sum(probs[trajectory][key]) > 0:
                    combined[trajectory][key].extend(probs[trajectory][key])
                else:
                    combined[trajectory][key].append(0.0)
    return combined

# filename = 'testing_cooccur-' + experiment_time + '.png'
# savepath = os.path.join(output_filepath, filename)
# plot_cooccur(probs, savepath=None)


# infos = [r063d2, r063d3]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6,
         r066d1, r066d2, r066d3, r066d4, r066d5,
         r067d1, r067d2, r067d3, r067d4, r067d5,
         r068d1, r068d2, r068d3, r068d4, r068d5, r068d6]

# Plot experiment phases separately
if 0:
    experiment_time = 'pauseA'
    all_probs_a, n_epochs_a = get_cooccur(infos, experiment_time)
    combined_weighted_a = combine_cooccur_weighted(all_probs_a, n_epochs_a)
    combined_a = combine_cooccur(all_probs_a, n_epochs_a)

    filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '.png'
    savepath_weighted = os.path.join(output_filepath, filename_weighted)
    plot_cooccur_combined(combined_weighted_a, np.sum(n_epochs_a), savepath_weighted)

    filename = 'combined_cooccur-' + experiment_time + '.png'
    savepath = os.path.join(output_filepath, filename)
    plot_cooccur(combined_a, savepath)


    experiment_time = 'pauseB'
    all_probs_b, n_epochs_b = get_cooccur(infos, experiment_time)
    combined_weighted_b = combine_cooccur_weighted(all_probs_b, n_epochs_b)
    combined_b = combine_cooccur(all_probs_b, n_epochs_b)

    filename_weighted = 'combined_weighted_cooccur-' + experiment_time + '.png'
    savepath_weighted = os.path.join(output_filepath, filename_weighted)
    plot_cooccur_combined(combined_weighted_b, np.sum(n_epochs_b), savepath_weighted)

    filename = 'combined_cooccur-' + experiment_time + '.png'
    savepath = os.path.join(output_filepath, filename)
    plot_cooccur(combined_b, savepath)

# Plot two phase's probs together in the same plot
if 1:
    experiment_times = ['pauseA', 'pauseB']
    all_probs_a, n_epochs_a = get_cooccur(infos, experiment_times[0])
    combined_weighted_a = combine_cooccur_weighted(all_probs_a, n_epochs_a)

    all_probs_b, n_epochs_b = get_cooccur(infos, experiment_times[1])
    combined_weighted_b = combine_cooccur_weighted(all_probs_b, n_epochs_b)

    filename = 'pauses-combined_cooccur.png'
    savepath = os.path.join(output_filepath, filename)
    plot_cooccur_weighted_pauses(combined_weighted_a, n_epochs_a, combined_weighted_b, n_epochs_b, experiment_times,
                        prob='zscore', ylabel='SWR co-activation z-scored', savepath=savepath)
