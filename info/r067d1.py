import os
import numpy as np
import nept
import info.meta

rat_id = 'R067_EI'
session_id = 'R067d1'
session = 'R067-2014-11-29'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC09b.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(10.285714285714285, 202.28571428571428+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-2.857142857142857, 141.14285714285714+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([9479.9, 9783.7]))
task_times['phase1'] = nept.Epoch(np.array([9858.4, 10462.3]))
task_times['pauseA'] = nept.Epoch(np.array([10526.9, 11128.7]))
task_times['phase2'] = nept.Epoch(np.array([11172.0, 12397.8]))
task_times['pauseB'] = nept.Epoch(np.array([12445.3, 14248.4]))
task_times['phase3'] = nept.Epoch(np.array([14338.9, 16559.5]))
task_times['postrecord'] = nept.Epoch(np.array([16631.5, 17040.7]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [177.7, 16.]
path_pts['turn1'] = [59.7, 15.1]
path_pts['turn2'] = [55.9, 100.]
path_pts['turn3'] = [151.8, 106.7]
path_pts['feeder2'] = [152., 133.7]
path_pts['shortcut1'] = [119., 13.2]
path_pts['spt1'] = [119., 56.7]
path_pts['shortcut2'] = [119., 106.5]
path_pts['novel1'] = [56.4, 45.2]
path_pts['npt1'] = [27.1, 45.8]
path_pts['novel2'] = [26.7, 102.]
path_pts['pedestal'] = [87.6, 61.8]
path_pts['stable1'] = [84.9, 109.4]

problem_positions = nept.Epoch(np.array([[10353.0, 10384.0]]))

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'novel1', 'turn2', 'shortcut2',
                                      'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['shortcut1', 'turn1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[16744.2, 16745.0]]))
sequence['u']['run'] = nept.Epoch(np.array([[16056.0, 16100.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[16843.9, 16844.2]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[15529.0, 15573.0]]))
sequence['shortcut']['ms'] = 10
