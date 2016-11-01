import os

from load_data import get_pos, get_events
from analyze_maze import get_trial_idx, get_zones
from analyze_plotting import plot_proportions, plot_bydurations, plot_bytrial

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'behavior')


outputs = [
    os.path.join(output_filepath, 'shortcut_behaviour_proportions.png'),
    os.path.join(output_filepath, 'shortcut_behaviour_durations.png'),
    os.path.join(output_filepath, 'shortcut_behaviour_bytrial.png')]


def analyze(infos, filename, figsize='normal'):
    durations = dict(u=[], shortcut=[], novel=[])
    num_sessions = 0

    trials = []

    for info in infos:
        print(info.session_id)
        t_start = info.task_times['phase3'].start
        t_stop = info.task_times['phase3'].stop

        pos = get_pos(info.pos_mat, info.pxl_to_cm)
        sliced_pos = pos.time_slice(t_start, t_stop)

        # Slicing events to only Phase 3
        events = get_events(info.event_mat)

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

        num_sessions += 1

        for key in durations:
            for trial in trials_idx[key]:
                durations[key].append(trials_idx['stop_trials'][trial[0]] - trials_idx['start_trials'][trial[0]])

    durations['num_sessions'] = num_sessions

    shortcuts = []
    us = []
    novels = []
    togethers = []

    for trial in trials:
        shortcuts.append(len(trial['shortcut'])/float(len(trial['start_trials'])))
        us.append(len(trial['u'])/float(len(trial['start_trials'])))
        novels.append(len(trial['novel'])/float(len(trial['start_trials'])))
        togethers.append(sorted(trial['u'] + trial['shortcut'] + trial['novel']))

    savename = filename + '_proportions.pdf'
    savepath = os.path.join(output_filepath, savename)
    if figsize == 'small':
        plot_proportions(us, shortcuts, novels, savepath, figsize=(2.5, 2))
    else:
        plot_proportions(us, shortcuts, novels, savepath)

    savename = filename + '_durations.pdf'
    savepath = os.path.join(output_filepath, savename)
    if figsize == 'small':
        plot_bydurations(durations, savepath, figsize=(2.5, 2))
    else:
        plot_bydurations(durations, savepath)

    savename = filename + '_bytrial.pdf'
    savepath = os.path.join(output_filepath, savename)
    if figsize == 'small':
        plot_bytrial(togethers, savepath, figsize=(3., 2))
    else:
        plot_bytrial(togethers, savepath)


if __name__ == "__main__":
    from run import (behavior_infos,
                     days1234_infos, days5678_infos,
                     r063_infos, r066_infos, r067_infos, r068_infos,
                     day1_infos, day2_infos, day3_infos, day4_infos, day5_infos, day6_infos, day7_infos, day8_infos)

    analyze(behavior_infos, 'all_behaviour', figsize='small')
    # analyze(days1234_infos, 'early_behaviour', figsize='small')
    # analyze(days5678_infos, 'late_behaviour', figsize='small')

    # analyze(day1_infos, 'session1_behaviour')
    # analyze(day2_infos, 'session2_behaviour')
    # analyze(day3_infos, 'session3_behaviour')
    # analyze(day4_infos, 'session4_behaviour')
    # analyze(day5_infos, 'session5_behaviour')
    # analyze(day6_infos, 'session6_behaviour')
    # analyze(day7_infos, 'session7_behaviour')
    # analyze(day8_infos, 'session8_behaviour')
    #
    # analyze(r063_infos, 'R063_behaviour')
    # analyze(r066_infos, 'R066_behaviour')
    # analyze(r067_infos, 'R067_behaviour')
    # analyze(r068_infos, 'R068_behaviour')
