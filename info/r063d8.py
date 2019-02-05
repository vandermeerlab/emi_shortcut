import os
import numpy as np
import nept
import info.meta

rat_id = 'R063_EI'
session_id = 'R063d8'
session = 'R063-2015-03-27'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC14a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC11a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(28.705882352941178, 208.70588235294113+info.meta.binsize, info.meta.binsize)
yedges = np.arange(4.588235294117647, 148.58823529411762+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([1393.0], [1696.3])
task_times['phase1'] = nept.Epoch([1734.8], [2232.3])
task_times['pauseA'] = nept.Epoch([2264.5], [2894.2])
task_times['phase2'] = nept.Epoch([2929.5], [4140.9])
task_times['pauseB'] = nept.Epoch([4159.0], [5981.2])
task_times['phase3'] = nept.Epoch([6006.2], [9044.7])
task_times['postrecord'] = nept.Epoch([9070.2], [9372.6])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [194.1, 13.5]
path_pts['turn1'] = [75.7, 20.8]
path_pts['pt1'] = [71.2, 62.8]
path_pts['turn2'] = [74.5, 106.2]
path_pts['pt2'] = [110.1, 115.3]
path_pts['pt3'] = [134.7, 113.7]
path_pts['turn3'] = [169.5, 108.3]
path_pts['feeder2'] = [170., 135.9]
path_pts['shortcut1'] = [194.1, 13.5]
path_pts['spt1'] = [199.2, 70.5]
path_pts['spt2'] = [175., 79.8]
path_pts['shortcut2'] = [169.5, 108.3]
path_pts['novel1'] = [74.5, 106.2]
path_pts['npt1'] = [72.5, 136.4]
path_pts['npt2'] = [40.6, 138.3]
path_pts['novel2'] = [39.5, 106.8]
path_pts['pedestal'] = [124.2, 53.5]
path_pts['stable1'] = [128.2, 11.7]

problem_positions = nept.Epoch([4250.872343], [4251.039648])

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2', 'pt2', 'pt3',
                                      'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

lfp_z_thresh = 1.5
