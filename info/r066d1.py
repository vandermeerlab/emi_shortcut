import os
import numpy as np
import nept
from utils_maze import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d1'
session = 'R066-2014-11-27'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

event_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-Events.nev')
event_labels = dict(led1='TTL Output on AcqSystem1_0 board 0 port 2 value (0x0001).',
                    led2='TTL Output on AcqSystem1_0 board 0 port 2 value (0x0002).',
                    ledoff='TTL Output on AcqSystem1_0 board 0 port 2 value (0x0000).',
                    pb1id='TTL Input on AcqSystem1_0 board 0 port 1 value (0x0040).',
                    pb2id='TTL Input on AcqSystem1_0 board 0 port 1 value (0x0020).',
                    pboff='TTL Input on AcqSystem1_0 board 0 port 1 value (0x0000).',
                    feeder1='TTL Output on AcqSystem1_0 board 0 port 0 value (0x0004).',
                    feeder2='TTL Output on AcqSystem1_0 board 0 port 0 value (0x0040).',
                    feederoff='TTL Output on AcqSystem1_0 board 0 port 0 value (0x0000).')

position_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-VT1.nvt')

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([15415.0, 15716.0]))
task_times['phase1'] = nept.Epoch(np.array([15792.0, 16397.0]))
task_times['pauseA'] = nept.Epoch(np.array([16465.0, 18860.0]))
task_times['phase2'] = nept.Epoch(np.array([19589.0, 22292.0]))
task_times['pauseB'] = nept.Epoch(np.array([22353.0, 24156.0]))
task_times['phase3'] = nept.Epoch(np.array([24219.0, 26922.0]))
task_times['postrecord'] = nept.Epoch(np.array([26960, 27263]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.6286, 7.1722)
scale_targets = (3.8, 3.5)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [524, 466]
path_pts['pt1'] = [529, 409]
path_pts['turn1'] = [523, 376]
path_pts['pt2'] = [473, 378]
path_pts['pt3'] = [416, 388]
path_pts['pt4'] = [347, 390]
path_pts['pt5'] = [313, 368]
path_pts['pt6'] = [279, 398]
path_pts['pt7'] = [229, 376]
path_pts['pt8'] = [183, 363]
path_pts['pt9'] = [192, 306]
path_pts['pt10'] = [195, 109]
path_pts['turn2'] = [204, 45]
path_pts['pt11'] = [261, 47]
path_pts['pt12'] = [294, 34]
path_pts['pt13a'] = [416, 48]
path_pts['pt13'] = [515, 40]
path_pts['pt14'] = [604, 74]
path_pts['feeder2'] = [643, 66]
path_pts['shortcut1'] = [416, 388]
path_pts['spt1'] = [415, 217]
path_pts['shortcut2'] = [416, 48]
path_pts['novel1'] = [204, 168]
path_pts['npt1'] = [111, 163]
path_pts['npt2'] = [95, 185]
path_pts['novel2'] = [90, 370]
path_pts['pedestal'] = [553, 212]
path_pts['stable1'] = [245, 375]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'pt7', 'pt8',
                                           'pt9', 'pt10', 'turn2', 'pt11', 'pt12', 'pt13', 'pt14', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt3', 'pt4', 'pt5', 'pt6', 'pt7', 'pt8', 'pt9', 'pt10',
                                      'turn2', 'pt11', 'pt12', 'pt13a']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[27229.75, 27230],
                                           [27082.1, 27082.5]]))
sequence['u']['run'] = nept.Epoch(np.array([[20480, 20510],
                                           [20588.5, 20618.5]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[26988.75, 26989],
                                                  [27019, 27019.6]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[24700, 24730],
                                                  [24755, 24785]]))
sequence['shortcut']['ms'] = 10

