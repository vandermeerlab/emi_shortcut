import os
import numpy as np
import nept
import info.meta

rat_id = 'R067_EI'
session_id = 'R067d6'
session = 'R067-2014-12-05'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(39.58823529411765, 207.58823529411765+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-0.117647058823529, 143.88235294117646+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([901.0, 1202.9]))
task_times['phase1'] = nept.Epoch(np.array([1252.5, 1760.8]))
task_times['pauseA'] = nept.Epoch(np.array([1779.0, 2436.1]))
task_times['phase2'] = nept.Epoch(np.array([2466.0, 3723.5]))
task_times['pauseB'] = nept.Epoch(np.array([3723.5, 5603.2]))
task_times['phase3'] = nept.Epoch(np.array([5636.8, 8385.6]))
task_times['postrecord'] = nept.Epoch(np.array([8412.9, 8716.6]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [184.7, 18.8]
path_pts['pt1'] = [116.2, 14.3]
path_pts['turn1'] = [64.5, 19.8]
path_pts['turn2'] = [60.1, 101.]
path_pts['pt2'] = [121., 113.2]
path_pts['turn3'] = [155., 111.5]
path_pts['feeder2'] = [152.9, 138.8]
path_pts['shortcut1'] = [155.2, 16.3]
path_pts['spt1'] = [153.4, 76.2]
path_pts['spt2'] = [123.6, 80.2]
path_pts['spt3'] = [82.8, 83.6]
path_pts['shortcut2'] = [89.1, 110.7]
path_pts['novel1'] = [60.1, 101.]
path_pts['novel2'] = [57.3, 137.6]
path_pts['pedestal'] = [103.6, 45.9]
path_pts['stable1'] = [58.4, 60.2]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'pt1', 'turn1', 'stable1', 'turn2',
                                      'shortcut2', 'pt2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt1', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]

lfp_z_thresh = 1.5
