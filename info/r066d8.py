import os
import numpy as np
import nept

rat_id = 'R066_EI'
session_id = 'R066d8'
session = 'R066-2014-12-05'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([14035.0, 14339.0]))
task_times['phase1'] = nept.Epoch(np.array([14395.0, 14916.0]))
task_times['pauseA'] = nept.Epoch(np.array([14941.0, 15544.0]))
task_times['phase2'] = nept.Epoch(np.array([15586.0, 16833.0]))
task_times['pauseB'] = nept.Epoch(np.array([16910.0, 18739.0]))
task_times['phase3'] = nept.Epoch(np.array([18772.0, 22184.0]))
task_times['postrecord'] = nept.Epoch(np.array([22237.0, 22568.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [184.1, 17.6]
path_pts['turn1'] = [62.5, 25.]
path_pts['pt1'] = [58.5, 46.5]
path_pts['pt2'] = [57., 80.8]
path_pts['turn2'] = [59.1, 100.1]
path_pts['pt3'] = [91.7, 112.9]
path_pts['turn3'] = [153.8, 110.3]
path_pts['feeder2'] = [152.4, 138.8]
path_pts['shortcut1'] = [157.3, 15.5]
path_pts['spt1'] = [156.5, 68.5]
path_pts['spt2'] = [141.3, 79.8]
path_pts['spt3'] = [127.1, 85.7]
path_pts['shortcut2'] = [127.1, 109.5]
path_pts['novel1'] = [59.1, 100.1]
path_pts['npt1'] = [58.3, 135.9]
path_pts['novel2'] = [26.8, 135.9]
path_pts['pedestal'] = [95.5, 54.6]
path_pts['stable1'] = [112.4, 13.2]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'stable1', 'pt1', 'pt2', 'turn2',
                                      'pt3', 'shortcut2', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
