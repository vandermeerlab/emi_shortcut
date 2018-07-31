import os
import numpy as np
import nept
import info.meta

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

xedges = np.arange(59.484469639179764, 227.48446963917976+info.meta.binsize, info.meta.binsize)
yedges = np.arange(11.390716236029345, 155.39071623602933+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([939.9, 1241.8]))
task_times['phase1'] = nept.Epoch(np.array([1279.1, 1761.1]))
task_times['pauseA'] = nept.Epoch(np.array([1786.6, 2390.0]))
task_times['phase2'] = nept.Epoch(np.array([2416.8, 3723.5]))
task_times['pauseB'] = nept.Epoch(np.array([3741.3, 5564.9]))
task_times['phase3'] = nept.Epoch(np.array([5636.7, 8682.6]))
task_times['postrecord'] = nept.Epoch(np.array([8713.2, 9049.1]))

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
path_pts['error'] = [[35., 10.], [135., -12.]]

problem_positions = nept.Epoch(np.array([[6199.592711, 6279.716461],
                                         [6513.185586, 6557.480055],
                                         [6855.730149, 6893.134649]]))
position_problem_location = [85., 20.]

u_trajectory = [path_pts[i] for i in ['feeder1', 'novel1', 'shortcut1', 'turn1', 'pt1', 'turn2',
                                      'shortcut2', 'stable1', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
