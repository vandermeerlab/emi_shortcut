import os
import numpy as np
import nept
import info.meta

rat_id = 'R067_EI'
session_id = 'R067d2'
session = 'R067-2014-12-01'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(10.428571428571429, 202.42857142857144+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-3.0, 141.0+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([33194.2, 33497.6]))
task_times['phase1'] = nept.Epoch(np.array([33554.8, 34158.0]))
task_times['pauseA'] = nept.Epoch(np.array([34210.4, 34812.5]))
task_times['phase2'] = nept.Epoch(np.array([34851.6, 36073.5]))
task_times['pauseB'] = nept.Epoch(np.array([36141.7, 37954.8]))
task_times['phase3'] = nept.Epoch(np.array([37993.0, 40758.4]))
task_times['postrecord'] = nept.Epoch(np.array([40817.0, 41135.3]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [177.7, 16.]
path_pts['turn1'] = [62.5, 17.3]
path_pts['pt1'] = [59., 56.8]
path_pts['turn2'] = [58., 102.]
path_pts['pt2'] = [86.6, 109.7]
path_pts['pt3'] = [114.3, 108.9]
path_pts['turn3'] = [151.3, 106.]
path_pts['feeder2'] = [149.7, 133.1]
path_pts['shortcut1'] = [177.7, 16.]
path_pts['spt1'] = [179.9, 47.]
path_pts['spt2'] = [151.5, 48.6]
path_pts['spt3'] = [151.2, 77.7]
path_pts['shortcut2'] = [151.3, 106.]
path_pts['novel1'] = [58., 102.]
path_pts['npt1'] = [28.2, 99.3]
path_pts['novel2'] = [30.5, 44.6]
path_pts['pedestal'] = [104.5, 56.4]
path_pts['stable1'] = [113.5, 11.8]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2', 'pt2', 'pt3', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['run'] = nept.Epoch(np.array([[35247.0, 35269.0],
                                           [35022.0, 35062.0]]))

sequence['u']['swr'] = nept.Epoch(np.array([[38650.8, 38651.6],
                                           [39172.3, 39172.9],
                                           [39310.6, 39311.2],
                                           [40108.2, 40108.9],
                                           [40240.6, 40241.5],
                                           [40681.8, 40682.5]]))

sequence['shortcut']['run'] = nept.Epoch(np.array([[35247.0, 35269.0]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[38650.8, 38651.6]]))

lfp_z_thresh = 2.0
