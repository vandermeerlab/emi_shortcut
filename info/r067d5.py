import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R067_EI'
session_id = 'R067d5'
session = 'R067-2014-12-04'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC05c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([12442.0, 12745.0]))
task_times['phase1'] = nept.Epoch(np.array([12778.0, 13371.0]))
task_times['pauseA'] = nept.Epoch(np.array([13402.0, 14013.0]))
task_times['phase2'] = nept.Epoch(np.array([14075.0, 15295.0]))
task_times['pauseB'] = nept.Epoch(np.array([15331.0, 17132.0]))
task_times['phase3'] = nept.Epoch(np.array([17170.0, 20303.0]))
task_times['postrecord'] = nept.Epoch(np.array([20337.0, 20669.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.3362, 7.1535)
scale_targets = (3.6, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [527, 460]
path_pts['pt1'] = [527, 415]
path_pts['turn1'] = [525, 374]
path_pts['pt2'] = [461, 377]
path_pts['pt3'] = [385, 388]
path_pts['pt4'] = [328, 394]
path_pts['pt5'] = [304, 379]
path_pts['pt6'] = [221, 360]
path_pts['turn2'] = [199, 356]
path_pts['pt7'] = [197, 323]
path_pts['pt8'] = [199, 209]
path_pts['pt9'] = [206, 89]
path_pts['turn3'] = [207, 65]
path_pts['pt10'] = [231, 56]
path_pts['pt11'] = [322, 43]
path_pts['pt11a'] = [407, 53]
path_pts['pt12'] = [512, 46]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [304, 379]
path_pts['spt1'] = [304, 222]
path_pts['spt2'] = [310, 179]
path_pts['spt3'] = [326, 152]
path_pts['spt4'] = [350, 145]
path_pts['spt5'] = [392, 144]
path_pts['spt6'] = [407, 131]
path_pts['shortcut2'] = [407, 53]
path_pts['novel1'] = [207, 65]
path_pts['npt1'] = [97, 77]
path_pts['novel2'] = [97, 193]
path_pts['pedestal'] = [545, 248]
path_pts['stable1'] = [198, 268]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6',
                                           'turn2', 'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt5', 'pt6', 'turn2', 'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt11a']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'spt6', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
