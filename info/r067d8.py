import os
import numpy as np
import nept
from utils_maze import convert_to_cm

rat_id = 'R067_EI'
session_id = 'R067d8'
session = 'R067-2014-12-07'

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
task_times['prerecord'] = nept.Epoch(np.array([513.2856, 817.4131]))
task_times['phase1'] = nept.Epoch(np.array([851.5246, 1337.7]))
task_times['pauseA'] = nept.Epoch(np.array([1359.0, 1961.6]))
task_times['phase2'] = nept.Epoch(np.array([2007.2, 3209.6]))
task_times['pauseB'] = nept.Epoch(np.array([3280.4, 5121.1]))
task_times['phase3'] = nept.Epoch(np.array([5156.7, 8459.1]))
task_times['postrecord'] = nept.Epoch(np.array([8482.3, 8839.7]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.6795, 7.1253)
scale_targets = (3.8, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [525, 460]
path_pts['turn1'] = [527, 376]
path_pts['pt1'] = [456, 383]
path_pts['pt2'] = [369, 398]
path_pts['turn2'] = [200, 351]
path_pts['pt3'] = [198, 211]
path_pts['turn3'] = [213, 73]
path_pts['pt4'] = [254, 54]
path_pts['pt5'] = [361, 48]
path_pts['pt6'] = [534, 60]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [428, 382]
path_pts['spt1'] = [423, 311]
path_pts['spt2'] = [437, 282]
path_pts['spt3'] = [487, 267]
path_pts['spt4'] = [521, 248]
path_pts['spt5'] = [529, 159]
path_pts['shortcut2'] = [534, 60]
path_pts['novel1'] = [200, 351]
path_pts['npt1'] = [193, 473]
path_pts['novel2'] = [80, 466]
path_pts['pedestal'] = [348, 178]
path_pts['stable1'] = [198, 220]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'turn2', 'pt3', 'turn3',
                                           'pt4', 'pt5', 'pt6', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'turn2', 'pt3', 'turn3',
                                      'pt4', 'pt5', 'pt6', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
