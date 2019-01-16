import os
import numpy as np
import nept
import info.meta

rat_id = 'R068_EI'
session_id = 'R068d4'
session = 'R068-2014-12-06'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(11.142857142857142, 203.14285714285714+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-3.1428571428571432, 140.85714285714286+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1374.3, 1677.1]))
task_times['phase1'] = nept.Epoch(np.array([1706.3, 2232.4]))
task_times['pauseA'] = nept.Epoch(np.array([2265.3, 2868.2]))
task_times['phase2'] = nept.Epoch(np.array([2894.8, 4142.7]))
task_times['pauseB'] = nept.Epoch(np.array([4167.1, 5995.2]))
task_times['phase3'] = nept.Epoch(np.array([6034.0, 8743.0]))
task_times['postrecord'] = nept.Epoch(np.array([8780.8, 9129.2]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [179.4, 18.3]
path_pts['turn1'] = [61.4, 16.8]
path_pts['pt1'] = [57.7, 45.5]
path_pts['pt2'] = [56.4, 77.1]
path_pts['turn2'] = [60.2, 101.4]
path_pts['pt3'] = [119., 110.7]
path_pts['turn3'] = [151.6, 107.1]
path_pts['feeder2'] = [150.3, 134.8]
path_pts['shortcut1'] = [179.4, 18.3]
path_pts['spt1'] = [183.4, 65.]
path_pts['spt2'] = [180.6, 106.3]
path_pts['shortcut2'] = [151.6, 107.1]
path_pts['novel1'] = [86.2, 110.3]
path_pts['npt1'] = [85.4, 135.]
path_pts['npt2'] = [53.5, 135.8]
path_pts['novel2'] = [27.5, 135.4]
path_pts['pedestal'] = [106.5, 60.1]
path_pts['stable1'] = [117.3, 14.4]
path_pts['error'] = [[36., 6.5]]

problem_positions = nept.Epoch(np.array([[6033.6, 6034.],
                                         [6106.9, 6107.4],
                                         [7508.6, 7509.]]))

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'pt2', 'turn2', 'novel1',
                                      'pt3', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt2', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

lfp_z_thresh = 1.5
