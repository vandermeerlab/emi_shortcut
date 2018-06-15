import os
import numpy as np
import nept

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

scale_targets = 1.8

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [173.3, 16.1]
path_pts['turn1'] = [59., 17.]
path_pts['pt1'] = [54.1, 61.]
path_pts['turn2'] = [55., 101.]
path_pts['pt2'] = [114.4, 106.2]
path_pts['turn3'] = [146.2, 104.3]
path_pts['feeder2'] = [146.1, 131.1]
path_pts['shortcut1'] = [145., 14.5]
path_pts['spt1'] = [145.2, 73.5]
path_pts['spt2'] = [88., 77.4]
path_pts['shortcut2'] = [83.8, 103.5]
path_pts['novel1'] = [55., 101.]
path_pts['novel2'] = [53.4, 132.4]
path_pts['pedestal'] = [96.4, 41.5]
path_pts['pedestal1'] = [192., 78.]
path_pts['stable1'] = [100.9, 12.6]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'stable1', 'turn1', 'pt1', 'turn2',
                                      'shortcut2', 'pt2', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]
