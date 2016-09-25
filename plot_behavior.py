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


def analyze(infos):
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

    savepath = os.path.join(output_filepath, 'shortcut_behaviour_proportions.png')
    plot_proportions(us, shortcuts, novels, savepath)

    savepath = os.path.join(output_filepath, 'shortcut_behaviour_durations.png')
    plot_bydurations(durations, savepath)

    savepath = os.path.join(output_filepath, 'shortcut_behaviour_bytrial.png')
    plot_bytrial(togethers, savepath)


if __name__ == "__main__":
    from run import spike_sorted_infos
    analyze(spike_sorted_infos)
