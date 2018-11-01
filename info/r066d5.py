import os
import numpy as np
import nept
import info.meta

rat_id = 'R066_EI'
session_id = 'R066d5'
session = 'R066-2014-12-02'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC05b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(16.393939393939394, 220.3939393939394+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-2.393939393939394, 153.6060606060606+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1061.4, 1363.5]))
task_times['phase1'] = nept.Epoch(np.array([1407.6, 1822.4]))
task_times['pauseA'] = nept.Epoch(np.array([1852.3, 2456.8]))
task_times['phase2'] = nept.Epoch(np.array([2492.5, 3694.3]))
task_times['pauseB'] = nept.Epoch(np.array([3735.8, 5542.1]))
task_times['phase3'] = nept.Epoch(np.array([5578.7, 8584.4]))
task_times['postrecord'] = nept.Epoch(np.array([8674.2, 8976.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [189.1, 17.]
path_pts['turn1'] = [66.5, 17.1]
path_pts['turn2'] = [63.6, 103.2]
path_pts['pt1'] = [127.7, 115.6]
path_pts['turn3'] = [157.7, 112.4]
path_pts['feeder2'] = [158.8, 141.2]
path_pts['shortcut1'] = [124., 13.2]
path_pts['spt1'] = [121.7, 36.4]
path_pts['spt2'] = [94.2, 49.5]
path_pts['spt3'] = [92., 79.]
path_pts['shortcut2'] = [93.3, 115.]
path_pts['novel1'] = [66.5, 17.1]
path_pts['npt1'] = [31.7, 11.9]
path_pts['novel2'] = [29.4, 45.1]
path_pts['pedestal'] = [167.3, 76.3]
path_pts['stable1'] = [59.4, 62.3]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'stable1', 'turn2', 'shortcut2',
                                      'pt1', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'stable1', 'turn2', 'shortcut2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[1820, 1823]]))
sequence['u']['run'] = nept.Epoch(np.array([[1546, 1563]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[7295, 7298]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[6680, 6712]]))
