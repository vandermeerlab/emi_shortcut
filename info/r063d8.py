import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R063_EI'
session_id = 'R063d8'
session = 'R063-2015-03-27'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC04a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC09a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1393.0, 1696.4]))
task_times['phase1'] = nept.Epoch(np.array([1734.8, 2232.5]))
task_times['pauseA'] = nept.Epoch(np.array([2264.4, 2894.4]))
task_times['phase2'] = nept.Epoch(np.array([2928.3, 4141.0]))
task_times['pauseB'] = nept.Epoch(np.array([4159.0, 5981.2]))
task_times['phase3'] = nept.Epoch(np.array([6006.1, 9044.9]))
task_times['postrecord'] = nept.Epoch(np.array([9070.2, 9372.8]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.7494, 7.3318)
scale_targets = (3.9, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [574, 459]
path_pts['turn1'] = [574, 370]
path_pts['pt1'] = [489, 377]
path_pts['pt2'] = [416, 395]
path_pts['pt3'] = [353, 386]
path_pts['pt4'] = [280, 379]
path_pts['turn2'] = [252, 368]
path_pts['pt5'] = [242, 312]
path_pts['pt6'] = [241, 126]
path_pts['turn3'] = [252, 71]
path_pts['pt7'] = [285, 59]
path_pts['pt8'] = [393, 45]
path_pts['pt9'] = [446, 41]
path_pts['pt10'] = [558, 43]
path_pts['feeder2'] = [663, 49]
path_pts['shortcut1'] = [574, 370]
path_pts['spt1'] = [580, 311]
path_pts['spt2'] = [589, 283]
path_pts['spt3'] = [627, 262]
path_pts['spt4'] = [671, 250]
path_pts['spt5'] = [679, 228]
path_pts['shortcut2'] = [663, 49]
path_pts['novel1'] = [252, 368]
path_pts['npt1'] = [243, 447]
path_pts['npt2'] = [232, 471]
path_pts['novel2'] = [113, 476]
path_pts['pedestal'] = [418, 192]
path_pts['stable1'] = [237, 220]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'pt4', 'turn2', 'pt5', 'pt6',
                                           'turn3', 'pt7', 'pt8', 'pt9', 'pt10', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'pt4', 'turn2', 'pt5', 'pt6',
                                      'turn3', 'pt7', 'pt8', 'pt9', 'pt10', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
