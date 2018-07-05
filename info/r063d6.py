import os
import numpy as np
import nept

rat_id = 'R063_EI'
session_id = 'R063d6'
session = 'R063-2015-03-25'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1487.2, 1833.2]))
task_times['phase1'] = nept.Epoch(np.array([1884.6, 2341.9]))
task_times['pauseA'] = nept.Epoch(np.array([2357.9, 2964.9]))
task_times['phase2'] = nept.Epoch(np.array([2996.0, 4046.0]))
task_times['pauseB'] = nept.Epoch(np.array([4066.0, 6474.2]))
task_times['phase3'] = nept.Epoch(np.array([6498.2, 9593.4]))
task_times['postrecord'] = nept.Epoch(np.array([9611.6, 9913.8]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [197., 17.]
path_pts['turn1'] = [73.6, 21.2]
path_pts['pt1'] = [69., 47.1]
path_pts['pt2'] = [66.3, 80.4]
path_pts['turn2'] = [68.5, 107.4]
path_pts['pt3'] = [131.5, 118.]
path_pts['turn3'] = [165.4, 117.2]
path_pts['feeder2'] = [166.2, 143.]
path_pts['shortcut1'] = [169.7, 14.9]
path_pts['spt1'] = [170., 52.3]
path_pts['spt2'] = [168.1, 76.4]
path_pts['spt3'] = [135., 82.1]
path_pts['spt4'] = [102.5, 87.4]
path_pts['shortcut2'] = [98.6, 117.8]
path_pts['novel1'] = [68.5, 107.4]
path_pts['npt1'] = [66., 140.]
path_pts['novel2'] = [29., 142.2]
path_pts['pedestal'] = [115.5, 46.6]
path_pts['stable1'] = [115.9, 13.8]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'stable1', 'turn1', 'pt1', 'pt2',
                                      'turn2', 'shortcut2', 'pt3', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[9741.2, 9741.4],
                                           [9717, 9717.8]]))
sequence['u']['run'] = nept.Epoch(np.array([[7155, 7185],
                                           [3042, 3064]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[9276.93, 9277.21],
                                                  [9702, 9702.8]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[6710, 6730],
                                                  [7392, 7422]]))
