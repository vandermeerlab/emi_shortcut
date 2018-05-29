import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d6'
session = 'R066-2014-12-03'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC05c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([22586.0, 22887.0]))
task_times['phase1'] = nept.Epoch(np.array([22920.0, 23533.0]))
task_times['pauseA'] = nept.Epoch(np.array([23573.0, 24175.0]))
task_times['phase2'] = nept.Epoch(np.array([24217.0, 25480.0]))
task_times['pauseB'] = nept.Epoch(np.array([25513.0, 27340.0]))
task_times['phase3'] = nept.Epoch(np.array([27377.0, 30061.0]))
task_times['postrecord'] = nept.Epoch(np.array([30105.0, 30420.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.1209, 7.1628)
scale_targets = (3.6, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [519, 453]
path_pts['turn1'] = [523, 389]
path_pts['pt1'] = [429, 384]
path_pts['pt2'] = [306, 376]
path_pts['pt3'] = [251, 369]
path_pts['turn2'] = [201, 350]
path_pts['pt4'] = [193, 285]
path_pts['pt5'] = [202, 134]
path_pts['turn3'] = [218, 72]
path_pts['pt6'] = [269, 50]
path_pts['pt7'] = [437, 48]
path_pts['pt8'] = [536, 57]
path_pts['feeder2'] = [622, 62]
path_pts['shortcut1'] = [306, 376]
path_pts['spt1'] = [312, 305]
path_pts['spt2'] = [330, 281]
path_pts['spt3'] = [484, 267]
path_pts['spt4'] = [515, 249]
path_pts['spt5'] = [524, 187]
path_pts['shortcut2'] = [536, 57]
path_pts['novel1'] = [201, 350]
path_pts['novel2'] = [195, 459]
path_pts['pedestal'] = [349, 163]
path_pts['stable1'] = [198, 126]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'turn2', 'pt4', 'pt5', 'turn3',
                                           'pt6', 'pt7', 'pt8', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2', 'pt3', 'turn2', 'pt4', 'pt5', 'turn3',
                                      'pt6', 'pt7', 'pt8']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]

default = task_times['postrecord'].start

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[25074, 25077]]))
sequence['u']['run'] = nept.Epoch(np.array([[23100, 23150]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[29837, 29840]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[29046, 29111]]))
