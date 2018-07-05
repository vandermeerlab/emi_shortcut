import os
import numpy as np
import nept

rat_id = 'R067_EI'
session_id = 'R067d5'
session = 'R067-2014-12-04'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC05b.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([12442.5, 12744.9]))
task_times['phase1'] = nept.Epoch(np.array([12778.0, 13370.5]))
task_times['pauseA'] = nept.Epoch(np.array([13401.6, 14012.6]))
task_times['phase2'] = nept.Epoch(np.array([14074.7, 15294.9]))
task_times['pauseB'] = nept.Epoch(np.array([15330.6, 17131.8]))
task_times['phase3'] = nept.Epoch(np.array([17170.4, 20302.5]))
task_times['postrecord'] = nept.Epoch(np.array([20337.1, 20668.5]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [178.3, 16.]
path_pts['turn1'] = [59.6, 17.3]
path_pts['turn2'] = [57.7, 98.4]
path_pts['pt1'] = [119.6, 107.7]
path_pts['turn3'] = [150.3, 105.8]
path_pts['feeder2'] = [149.7, 133.1]
path_pts['shortcut1'] = [118.1, 14.3]
path_pts['spt1'] = [116.2, 38.5]
path_pts['spt2'] = [89.9, 45.]
path_pts['spt3'] = [87.4, 79.2]
path_pts['shortcut2'] = [88.1, 107.]
path_pts['novel1'] = [59.6, 17.3]
path_pts['npt1'] = [28.6, 23.5]
path_pts['novel2'] = [28.8, 54.4]
path_pts['pedestal'] = [155.6, 69.4]
path_pts['stable1'] = [58., 54.8]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'stable1', 'turn2', 'shortcut2',
                                      'pt1', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
