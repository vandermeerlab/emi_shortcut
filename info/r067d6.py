import os
import numpy as np
import nept
from utils_maze import convert_to_cm

rat_id = 'R067_EI'
session_id = 'R067d6'
session = 'R067-2014-12-05'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC08b.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([900.9675, 1203.0]))
task_times['phase1'] = nept.Epoch(np.array([1252.5, 1761.0]))
task_times['pauseA'] = nept.Epoch(np.array([1779.0, 2436.1]))
task_times['phase2'] = nept.Epoch(np.array([2465.9, 3723.5]))
task_times['pauseB'] = nept.Epoch(np.array([3723.5, 5603.5]))
task_times['phase3'] = nept.Epoch(np.array([5636.8, 8385.7]))
task_times['postrecord'] = nept.Epoch(np.array([8412.9, 8716.7]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.4689, 7.2098)
scale_targets = (3.7, 3.8)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [525, 445]
path_pts['turn1'] = [527, 360]
path_pts['pt1'] = [456, 365]
path_pts['pt2'] = [369, 380]
path_pts['pt2a'] = [304, 375]
path_pts['turn2'] = [200, 335]
path_pts['pt3'] = [198, 211]
path_pts['turn3'] = [213, 73]
path_pts['pt4'] = [254, 54]
path_pts['pt5'] = [361, 48]
path_pts['pt6'] = [534, 60]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [304, 375]
path_pts['spt1'] = [308, 310]
path_pts['spt2'] = [334, 277]
path_pts['spt3'] = [414, 274]
path_pts['spt4'] = [508, 268]
path_pts['spt5'] = [528, 241]
path_pts['spt6'] = [535, 164]
path_pts['shortcut2'] = [534, 60]
path_pts['novel1'] = [200, 335]
path_pts['novel2'] = [193, 455]
path_pts['pedestal'] = [351, 157]
path_pts['stable1'] = [204, 126]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt2a', 'turn2', 'pt3', 'turn3',
                                           'pt4', 'pt5', 'pt6', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2a', 'turn2', 'pt3', 'turn3', 'pt4', 'pt5', 'pt6']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'spt6', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]
