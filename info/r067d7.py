import os
import numpy as np
import nept
import info.meta

rat_id = 'R067_EI'
session_id = 'R067d7'
session = 'R067-2014-12-06'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(47.32258064516129, 227.32258064516128+info.meta.binsize, info.meta.binsize)
yedges = np.arange(11.702416810187803, 155.7024168101878+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([781.6], [1088.7])
task_times['phase1'] = nept.Epoch([1123.0], [1627.1])
task_times['pauseA'] = nept.Epoch([1641.9], [2253.3])
task_times['phase2'] = nept.Epoch([2301.6], [3515.9])
task_times['pauseB'] = nept.Epoch([3575.5], [5383.7])
task_times['phase3'] = nept.Epoch([5415.4], [7840.7])
task_times['postrecord'] = nept.Epoch([7860.9], [8168.0])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.55

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [202.5, 25.8]
path_pts['pt1'] = [157.2, 24.]
path_pts['turn1'] = [69.5, 28.2]
path_pts['pt2'] = [63.1, 70.]
path_pts['turn2'] = [63.9, 111.6]
path_pts['turn3'] = [170.2, 121.1]
path_pts['feeder2'] = [169.7, 152.3]
path_pts['shortcut1'] = [103.7, 23.6]
path_pts['spt1'] = [100., 46.3]
path_pts['spt2'] = [105.8, 75.1]
path_pts['spt3'] = [98.6, 101.2]
path_pts['shortcut2'] = [100.8, 122.8]
path_pts['novel1'] = [169., 24.]
path_pts['npt1'] = [168.8, 51.3]
path_pts['npt2'] = [134.7, 55.8]
path_pts['novel2'] = [131.6, 86.7]
path_pts['pedestal'] = [197., 89.5]
path_pts['pedestal1'] = [155.3, 78.5]
path_pts['stable1'] = [141.6, 121.5]

u_trajectory = [path_pts[i] for i in ['feeder1', 'novel1', 'pt1', 'shortcut1', 'turn1', 'pt2', 'turn2',
                                      'shortcut2', 'stable1', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'pt2', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

lfp_z_thresh = 1.5
