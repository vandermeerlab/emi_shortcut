import os
import numpy as np
import nept

rat_id = 'R066_EI'
session_id = 'R066d7'
session = 'R066-2014-12-04'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC08d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([939.9331, 1242.0]))
task_times['phase1'] = nept.Epoch(np.array([1279.1, 1761.1]))
task_times['pauseA'] = nept.Epoch(np.array([1786.4, 2390.3]))
task_times['phase2'] = nept.Epoch(np.array([2416.6, 3723.7]))
task_times['pauseB'] = nept.Epoch(np.array([3741.3, 5565.0]))
task_times['phase3'] = nept.Epoch(np.array([5636.6, 8682.7]))
task_times['postrecord'] = nept.Epoch(np.array([8713.1, 9049.3]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.55

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [202.6, 25.2]
path_pts['turn1'] = [68., 30.5]
path_pts['pt1'] = [61.8, 75.2]
path_pts['turn2'] = [67., 112.2]
path_pts['turn3'] = [169.2, 121.]
path_pts['feeder2'] = [169., 150.3]
path_pts['shortcut1'] = [102.7, 24.2]
path_pts['spt1'] = [103.6, 50.4]
path_pts['spt2'] = [106., 73.8]
path_pts['spt3'] = [100., 98.5]
path_pts['shortcut2'] = [103.1, 122.2]
path_pts['novel1'] = [171., 23.]
path_pts['npt1'] = [168.7, 50.4]
path_pts['npt2'] = [137.9, 56.9]
path_pts['novel2'] = [134.4, 86.3]
path_pts['pedestal'] = [194.3, 85.6]
path_pts['stable1'] = [139.4, 122.6]

u_trajectory = [path_pts[i] for i in ['feeder1', 'novel1', 'shortcut1', 'turn1', 'pt1', 'turn2',
                                      'shortcut2', 'stable1', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
