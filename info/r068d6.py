import os
import numpy as np
import nept
from utils_maze import convert_to_cm

rat_id = 'R068_EI'
session_id = 'R068d6'
session = 'R068-2014-12-08'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC09c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1622.4, 1923.8]))
task_times['phase1'] = nept.Epoch(np.array([1959.6, 2450.2]))
task_times['pauseA'] = nept.Epoch(np.array([2466.5, 3088.1]))
task_times['phase2'] = nept.Epoch(np.array([3155., 4629.2]))
task_times['pauseB'] = nept.Epoch(np.array([4657.3, 6482.3]))
task_times['phase3'] = nept.Epoch(np.array([6524.4, 9277.9]))
task_times['postrecord'] = nept.Epoch(np.array([9303.1, 9609.8]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.1989, 7.1159)
scale_targets = (3.6, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['pt1'] = [524, 409]
path_pts['turn1'] = [518, 373]
path_pts['pt2'] = [423, 381]
path_pts['pt3'] = [362, 394]
path_pts['pt3a'] = [306, 384]
path_pts['pt4'] = [274, 374]
path_pts['turn2'] = [199, 361]
path_pts['pt5'] = [202, 162]
path_pts['turn3'] = [207, 58]
path_pts['pt6'] = [302, 46]
path_pts['pt7'] = [422, 49]
path_pts['pt8'] = [525, 54]
path_pts['feeder2'] = [631, 58]
path_pts['shortcut1'] = [306, 384]
path_pts['spt1'] = [304, 309]
path_pts['spt2'] = [316, 286]
path_pts['spt3'] = [342, 276]
path_pts['spt4'] = [429, 272]
path_pts['spt5'] = [507, 270]
path_pts['spt6'] = [523, 255]
path_pts['spt7'] = [528, 196]
path_pts['shortcut2'] = [525, 54]
path_pts['novel1'] = [199, 361]
path_pts['novel2'] = [194, 476]
path_pts['pedestal'] = [363, 162]
path_pts['stable1'] = [198, 126]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt3a', 'pt4', 'turn2',
                                           'pt5', 'turn3', 'pt6', 'pt7', 'pt8', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt3a', 'pt4', 'turn2', 'pt5', 'turn3', 'pt6', 'pt7', 'pt8']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5',
                                             'spt6', 'spt7', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]
