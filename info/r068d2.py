import os
import numpy as np
import nept
import info.meta

rat_id = 'R068_EI'
session_id = 'R068d2'
session = 'R068-2014-12-04'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(7.857142857142858, 199.85714285714286+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-3.0, 141.0+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([762.8, 1067.0]))
task_times['phase1'] = nept.Epoch(np.array([1110.1, 1600.8]))
task_times['pauseA'] = nept.Epoch(np.array([1662.4, 2266.7]))
task_times['phase2'] = nept.Epoch(np.array([2328.4, 3544.6]))
task_times['pauseB'] = nept.Epoch(np.array([3582.9, 5416.6]))
task_times['phase3'] = nept.Epoch(np.array([5450.7, 8464.4]))
task_times['postrecord'] = nept.Epoch(np.array([8526.8, 8970.8]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [178.3, 16.]
path_pts['turn1'] = [60., 15.6]
path_pts['pt1'] = [57.8, 58.6]
path_pts['turn2'] = [58.2, 104.]
path_pts['pt2'] = [98.5, 113.5]
path_pts['turn3'] = [149.5, 104.7]
path_pts['feeder2'] = [149.7, 133.1]
path_pts['shortcut1'] = [178.3, 16.]
path_pts['spt1'] = [178.6, 44.3]
path_pts['spt2'] = [152., 51.]
path_pts['spt3'] = [151.5, 79.3]
path_pts['shortcut2'] = [149.5, 104.7]
path_pts['novel1'] = [58.2, 104.]
path_pts['npt1'] = [26.2, 102.8]
path_pts['novel2'] = [28.3, 46.7]
path_pts['pedestal'] = [96.9, 61.4]
path_pts['stable1'] = [115.4, 13.2]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2',
                                      'pt2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['run'] = nept.Epoch(np.array([[2458.4, 2498.4]]))

sequence['u']['swr'] = nept.Epoch(np.array([[7721.2, 7721.5]]))
