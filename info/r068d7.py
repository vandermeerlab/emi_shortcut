import os
import numpy as np
import nept

rat_id = 'R068_EI'
session_id = 'R068d7'
session = 'R068-2014-12-09'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([672.6674, 1000.1]))
task_times['phase1'] = nept.Epoch(np.array([1038.0, 1672.9]))
task_times['pauseA'] = nept.Epoch(np.array([1694.4, 2297.5]))
task_times['phase2'] = nept.Epoch(np.array([2325.0, 3591.7]))
task_times['pauseB'] = nept.Epoch(np.array([3643.7, 5479.5]))
task_times['phase3'] = nept.Epoch(np.array([5497.3, 8238.8]))
task_times['postrecord'] = nept.Epoch(np.array([8262.5, 8619.6]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [159.4, 143.]
path_pts['turn1'] = [63.7, 26.4]
path_pts['pt1'] = [59.5, 66.3]
path_pts['turn2'] = [63., 109.5]
path_pts['turn3'] = [157.3, 112.2]
path_pts['feeder2'] = [189., 21.8]
path_pts['shortcut1'] = [90.8, 23.9]
path_pts['spt1'] = [100.6, 67.6]
path_pts['shortcut2'] = [88.7, 112.5]
path_pts['novel1'] = [156.5, 20.9]
path_pts['npt1'] = [156.4, 45.3]
path_pts['npt2'] = [124.2, 48.2]
path_pts['novel2'] = [125.1, 78.5]
path_pts['pedestal'] = [182., 81.4]
path_pts['stable1'] = [126.4, 116.7]

u_trajectory = [path_pts[i] for i in ['feeder1', 'novel1', 'shortcut1', 'turn1', 'pt1', 'turn2',
                                      'shortcut2', 'stable1', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
