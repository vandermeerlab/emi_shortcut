import os
import numpy as np
import vdmlab as vdm

from load_data import get_pos, get_events
from maze_functions import get_trial_idx, get_zones
from plotting_functions import plot_proportions, plot_bydurations, plot_bytrial

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
output_filepath = os.path.join(thisdir, 'plots', 'behavior')

# infos = [r063d2, r063d3]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6,
         r066d1, r066d2, r066d3, r066d4, r066d5,
         r067d1, r067d2, r067d3, r067d4, r067d5,
         r068d1, r068d2, r068d3, r068d4, r068d5, r068d6]


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

savepath = os.path.join(output_filepath, 'shortcut_behavior_durations.png')
plot_bydurations(durations, savepath)

savepath = os.path.join(output_filepath, 'shortcut_behaviour_bytrial.png')
plot_bytrial(togethers, savepath)
