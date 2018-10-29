import os
import numpy as np
import nept
import info.meta

rat_id = 'R066_EI'
session_id = 'R066d6'
session = 'R066-2014-12-03'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(33.909090909090914, 213.9090909090909+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-2.757575757575758, 153.24242424242425+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([22586.2, 22887.2]))
task_times['phase1'] = nept.Epoch(np.array([22920.1, 23495.1]))
task_times['pauseA'] = nept.Epoch(np.array([23572.8, 24174.8]))
task_times['phase2'] = nept.Epoch(np.array([24217.4, 25480.2]))
task_times['pauseB'] = nept.Epoch(np.array([25513.0, 27339.6]))
task_times['phase3'] = nept.Epoch(np.array([27376.6, 30061.2]))
task_times['postrecord'] = nept.Epoch(np.array([30105.0, 30419.5]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [189., 17.]
path_pts['turn1'] = [66.5, 19.2]
path_pts['pt1'] = [60.7, 62.4]
path_pts['turn2'] = [61.9, 101.4]
path_pts['pt2'] = [126.5, 115.7]
path_pts['turn3'] = [158.8, 111.7]
path_pts['feeder2'] = [158.8, 141.2]
path_pts['shortcut1'] = [160.6, 15.4]
path_pts['spt1'] = [156.6, 75.3]
path_pts['spt2'] = [128.9, 80.8]
path_pts['spt3'] = [96.4, 87.9]
path_pts['shortcut2'] = [93.3, 113.1]
path_pts['novel1'] = [61.9, 101.4]
path_pts['novel2'] = [59.1, 142.5]
path_pts['pedestal'] = [105.4, 48.7]
path_pts['stable1'] = [114.6, 12.1]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'stable1', 'turn1', 'pt1', 'turn2',
                                      'shortcut2', 'pt2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt1', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]

default = task_times['postrecord'].start

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[25074, 25077]]))
sequence['u']['run'] = nept.Epoch(np.array([[23100, 23150]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[29837, 29840]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[29046, 29111]]))
