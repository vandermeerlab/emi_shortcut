import os
import numpy as np
import nept
import info.meta

rat_id = 'R068_EI'
session_id = 'R068d8'
session = 'R068-2014-12-10'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC03a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(7.793431941338881, 199.7934319413389+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-2.352941176470588, 141.64705882352942+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([553.2], [855.2])
task_times['phase1'] = nept.Epoch([903.7], [1512.5])
task_times['pauseA'] = nept.Epoch([1607.7], [2291.3])
task_times['phase2'] = nept.Epoch([2333.8], [3555.8])
task_times['pauseB'] = nept.Epoch([3586.1], [5440.6])
task_times['phase3'] = nept.Epoch([5479.7], [8480.2])
task_times['postrecord'] = nept.Epoch([8523.7], [8855.9])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [187., 19.4]
path_pts['pt1'] = [112.8, 18.5]
path_pts['turn1'] = [66., 19.]
path_pts['pt2'] = [88.8, 110.5]
path_pts['turn2'] = [62.2, 107.3]
path_pts['turn3'] = [153.5, 113.8]
path_pts['feeder2'] = [155., 136.5]
path_pts['shortcut1'] = [158.3, 18.5]
path_pts['spt1'] = [156.1, 76.9]
path_pts['spt2'] = [129.4, 85.9]
path_pts['shortcut2'] = [121.8, 109.]
path_pts['novel1'] = [62.2, 107.3]
path_pts['npt1'] = [58.7, 134.5]
path_pts['novel2'] = [34., 138.5]
path_pts['pedestal'] = [102.5, 55.8]
path_pts['stable1'] = [60., 60.]
path_pts['error'] = [[220., 40.]]

problem_positions = nept.Epoch([924.7], [924.9])

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'pt1', 'turn1', 'stable1', 'turn2',
                                      'pt2', 'shortcut2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

lfp_z_thresh = 1.5
