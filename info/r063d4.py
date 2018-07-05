import os
import numpy as np
import nept

rat_id = 'R063_EI'
session_id = 'R063d4'
session = 'R063-2015-03-23'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13b.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC04b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1074.6, 1378.5]))
task_times['phase1'] = nept.Epoch(np.array([1415.9, 1847.0]))
task_times['pauseA'] = nept.Epoch(np.array([1860.7, 2485.8]))
task_times['phase2'] = nept.Epoch(np.array([2504.6, 3704.4]))
task_times['pauseB'] = nept.Epoch(np.array([3725.3, 5600.5]))
task_times['phase3'] = nept.Epoch(np.array([5627.5, 8638.6]))
task_times['postrecord'] = nept.Epoch(np.array([8656.5, 8999.7]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [191.7, 16.5]
path_pts['pt1'] = [144.4, 13.5]
path_pts['turn1'] = [72., 20.]
path_pts['pt2'] = [65., 70.8]
path_pts['turn2'] = [66.2, 105.1]
path_pts['pt3'] = [126.1, 115.7]
path_pts['turn3'] = [162.7, 113.]
path_pts['feeder2'] = [161.2, 138.8]
path_pts['shortcut1'] = [191.7, 16.5]
path_pts['spt1'] = [194., 55.5]
path_pts['spt2'] = [191.3, 105.3]
path_pts['shortcut2'] = [162.7, 113.]
path_pts['novel1'] = [95.9, 115.7]
path_pts['npt1'] = [94.5, 139.7]
path_pts['npt2'] = [56.4, 140.3]
path_pts['novel2'] = [31., 138.5]
path_pts['pedestal'] = [120.7, 60.]
path_pts['stable1'] = [98.7, 13.5]

u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'stable1', 'turn1', 'pt2', 'turn2',
                                      'novel1', 'pt3', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[8876.4, 8876.7],
                                           [8855.0, 8855.4],
                                           [8965.4, 8966.0]]))
sequence['u']['run'] = nept.Epoch(np.array([[2577, 2607],
                                           [2668.0, 2698.0],
                                           [3632.0, 3667.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[8872.65, 8873.15],
                                                  [8578.9, 8579.5],
                                                  [8575.37, 8575.55],
                                                  [8119.5, 8119.8],
                                                  [8206.82, 8207.38]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[5760.0, 5790.0],
                                                  [6214.0, 6244.0],
                                                  [5900.0, 5945.0],
                                                  [6460.0, 6490.0],
                                                  [6510.0, 6550.0]]))
sequence['shortcut']['ms'] = 10
