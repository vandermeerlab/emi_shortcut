import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R068_EI'
session_id = 'R068d8'
session = 'R068-2014-12-10'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC03c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([553.1661, 855.2456]))
task_times['phase1'] = nept.Epoch(np.array([903.6441, 1512.7]))
task_times['pauseA'] = nept.Epoch(np.array([1607.6, 2291.4]))
task_times['phase2'] = nept.Epoch(np.array([2333.7, 3555.9]))
task_times['pauseB'] = nept.Epoch(np.array([3586.1, 5440.8]))
task_times['phase3'] = nept.Epoch(np.array([5479.6, 8480.2]))
task_times['postrecord'] = nept.Epoch(np.array([8523.6, 8855.9]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.6141, 6.9188)
scale_targets = (3.8, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['turn1'] = [527, 411]
path_pts['pt1'] = [488, 401]
path_pts['pt2'] = [424, 377]
path_pts['pt3'] = [349, 372]
path_pts['pt4'] = [262, 389]
path_pts['turn2'] = [206, 389]
path_pts['pt5'] = [210, 115]
path_pts['turn3'] = [232, 75]
path_pts['pt6'] = [276, 65]
path_pts['pt7'] = [541, 67]
path_pts['feeder2'] = [632, 72]
path_pts['shortcut1'] = [424, 377]
path_pts['spt1'] = [433, 316]
path_pts['spt2'] = [456, 285]
path_pts['spt3'] = [485, 280]
path_pts['spt4'] = [524, 269]
path_pts['spt5'] = [541, 230]
path_pts['shortcut2'] = [541, 67]
path_pts['novel1'] = [206, 389]
path_pts['npt1'] = [210, 464]
path_pts['novel2'] = [80, 469]
path_pts['pedestal'] = [346, 196]
path_pts['stable1'] = [201, 220]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'turn2',
                                           'pt5', 'turn3', 'pt6', 'pt7', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2', 'pt3', 'pt4', 'turn2', 'pt5', 'turn3', 'pt6', 'pt7']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
