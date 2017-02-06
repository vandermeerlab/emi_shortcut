import os
import pandas as pd
import numpy as np
import scipy.stats as stats

from loading_data import get_data
from utils_maze import get_trial_idx, get_zones
from utils_plotting import plot_proportions, plot_durations, plot_bytrial

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'behavior')


outputs = [
    os.path.join(output_filepath, 'shortcut_behaviour_proportions.png'),
    os.path.join(output_filepath, 'shortcut_behaviour_durations.png'),
    os.path.join(output_filepath, 'shortcut_behaviour_bytrial.png')]


def bytrial_counts(togethers, min_length):
    """Finds the behavioral choice by trial for all animals combined.

    Parameters
    ----------
    togethers : list
    min_length : int

    Returns
    -------
    means : dict
        With u, shortcut, novel as keys
    sems : dict
        With u, shortcut, novel as keys

    """
    bytrial = dict(u=[], shortcut=[], novel=[])
    for trial in range(min_length):
        for key in bytrial:
            bytrial[key].append([])

    for session in togethers:
        for trial in range(min_length):
            for key in bytrial:
                if session[trial][1] == key:
                    bytrial[key][trial].append(1)
                else:
                    bytrial[key][trial].append(0)

    means = dict(u=[], shortcut=[], novel=[])
    sems = dict(u=[], shortcut=[], novel=[])
    for trial in range(min_length):
        for key in bytrial:
            means[key].append(np.mean(bytrial[key][trial]))
            sems[key].append(stats.sem(bytrial[key][trial]))

    return means, sems


def combine_behavior(infos):
    durations = dict(u=[], shortcut=[], novel=[])
    n_sessions = 0

    trials = []
    togethers = []

    for info in infos:
        print(info.session_id)

        events, position, spikes, lfp, lfp_theta = get_data(info)

        t_start = info.task_times['phase3'].start
        t_stop = info.task_times['phase3'].stop

        sliced_pos = position.time_slice(t_start, t_stop)

        feeder1_times = []
        for feeder1 in events['feeder1']:
            if t_start < feeder1 < t_stop:
                feeder1_times.append(feeder1)

        feeder2_times = []
        for feeder2 in events['feeder2']:
            if t_start < feeder2 < t_stop:
                feeder2_times.append(feeder2)

        path_pos = get_zones(info, sliced_pos)

        trials_idx = get_trial_idx(path_pos['u'].time, path_pos['shortcut'].time, path_pos['novel'].time,
                                   feeder1_times, feeder2_times, t_stop)

        trials.append(trials_idx)

        n_sessions += 1

        for key in durations:
            for trial in trials_idx[key]:
                durations[key].append(trials_idx['stop_trials'][trial[0]] - trials_idx['start_trials'][trial[0]])

        for trial in trials:
            togethers.append(sorted(trial['u'] + trial['shortcut'] + trial['novel']))

    return durations, trials, togethers, n_sessions


if __name__ == "__main__":
    from run import (behavior_infos,
                     days1234_infos, days5678_infos,
                     r063_infos, r066_infos, r067_infos, r068_infos,
                     day1_infos, day2_infos, day3_infos, day4_infos, day5_infos, day6_infos, day7_infos, day8_infos,
                     spike_sorted_infos)

    if 1:
        infos = behavior_infos

        proportion_filename = 'all-behavior_proportions.png'
        duration_filename = 'all-behavior_durations.png'
        bytrial_filename = 'all-behavior_bytrial.png'

        total_n_sessions = 0

        durations_together = dict(trajectory=[], value=[])
        trials_together = dict(trajectory=[], value=[])

        durations, trials, togethers, n_sessions = combine_behavior(infos)
        total_n_sessions += n_sessions

        for key in durations:
            for val in durations[key]:
                durations_together['trajectory'].append(key)
                durations_together['value'].append(val)

        for key in ['u', 'shortcut', 'novel']:
            for trial in trials:
                trials_together['trajectory'].append(key)
                trials_together['value'].append(len(trial[key])/float(len(trial['start_trials'])))

        df_durations = pd.DataFrame(data=durations_together)
        df_trials = pd.DataFrame(data=trials_together)

        proportion_savepath = os.path.join(output_filepath, proportion_filename)
        plot_proportions(df_trials, proportion_savepath, total_n_sessions, early_late=False, figsize=(8, 5), savefig=True)

        duration_savepath = os.path.join(output_filepath, duration_filename)
        plot_durations(df_durations, duration_savepath, total_n_sessions, early_late=False, figsize=(8, 5), fliersize=3, savefig=True)

        min_length = 30
        means, sems = bytrial_counts(togethers, min_length)

        bytrial_savepath = os.path.join(output_filepath, bytrial_filename)
        plot_bytrial(means, sems, total_n_sessions, bytrial_savepath, figsize=(8, 5), savefig=True)

    if 1:
        total_n_sessions = 0

        durations_together = dict(trajectory=[], value=[], time=[])
        trials_together = dict(trajectory=[], value=[], time=[])

        durations, trials, togethers, n_sessions = combine_behavior(days1234_infos)
        total_n_sessions += n_sessions

        for key in durations:
            for val in durations[key]:
                durations_together['trajectory'].append(key)
                durations_together['value'].append(val)
                durations_together['time'].append('early 1-4')

        for key in ['u', 'shortcut', 'novel']:
            for trial in trials:
                trials_together['trajectory'].append(key)
                trials_together['value'].append(len(trial[key])/float(len(trial['start_trials'])))
                trials_together['time'].append('early 1-4')

        min_length = 30
        means, sems = bytrial_counts(togethers, min_length)
        bytrial_filename = 'early_durations.png'
        bytrial_savepath = os.path.join(output_filepath, bytrial_filename)
        plot_bytrial(means, sems, total_n_sessions, bytrial_savepath, figsize=(8, 5), savefig=True)

        durations, trials, togethers, n_sessions = combine_behavior(days5678_infos)
        total_n_sessions += n_sessions

        for key in durations:
            for val in durations[key]:
                durations_together['trajectory'].append(key)
                durations_together['value'].append(val)
                durations_together['time'].append('later 5-8')

        for key in ['u', 'shortcut', 'novel']:
            for trial in trials:
                trials_together['trajectory'].append(key)
                trials_together['value'].append(len(trial[key])/float(len(trial['start_trials'])))
                trials_together['time'].append('later 5-8')


        df_durations = pd.DataFrame(data=durations_together)
        df_trials = pd.DataFrame(data=trials_together)

        filename = 'early-late_proportions.png'
        savepath = os.path.join(output_filepath, filename)
        plot_proportions(df_trials, savepath, total_n_sessions, early_late=True, figsize=(8, 5), savefig=True)

        filename = 'early-late_durations.png'
        savepath = os.path.join(output_filepath, filename)
        plot_durations(df_durations, savepath, total_n_sessions, early_late=True, figsize=(8, 5), fliersize=3, savefig=True)

        min_length = 30
        means, sems = bytrial_counts(togethers, min_length)
        bytrial_filename = 'later_durations.png'
        bytrial_savepath = os.path.join(output_filepath, bytrial_filename)
        plot_bytrial(means, sems, total_n_sessions, bytrial_savepath, figsize=(8, 5), savefig=True)
