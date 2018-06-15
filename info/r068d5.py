import os
import numpy as np
import nept

rat_id = 'R068_EI'
session_id = 'R068d5'
session = 'R068-2014-12-07'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC09a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC16c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([972.4348, 1282.5]))
task_times['phase1'] = nept.Epoch(np.array([1318.8, 1938.0]))
task_times['pauseA'] = nept.Epoch(np.array([1986.8, 2609.1]))
task_times['phase2'] = nept.Epoch(np.array([2638.1, 3870.7]))
task_times['pauseB'] = nept.Epoch(np.array([3887.5, 5708.9]))
task_times['phase3'] = nept.Epoch(np.array([5765.6, 8505.5]))
task_times['postrecord'] = nept.Epoch(np.array([8545.3, 8887.3]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [178.3, 16.6]
path_pts['turn1'] = [60., 15.]
path_pts['turn2'] = [59.1, 101.6]
path_pts['turn3'] = [152.2, 107.7]
path_pts['feeder2'] = [150.3, 134.9]
path_pts['shortcut1'] = [117.7, 16.3]
path_pts['spt1'] = [111., 38.2]
path_pts['spt2'] = [89.8, 45.6]
path_pts['spt3'] = [86.6, 79.7]
path_pts['shortcut2'] = [86.7, 106.9]
path_pts['novel1'] = [60., 15.]
path_pts['npt1'] = [29., 20.8]
path_pts['novel2'] = [29.7, 50.]
path_pts['pedestal'] = [145.6, 69.1]
path_pts['stable1'] = [57.2, 59.]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'stable1', 'turn2', 'shortcut2',
                                      'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
