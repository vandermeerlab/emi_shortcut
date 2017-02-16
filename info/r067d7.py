import os
import numpy as np
import nept
from startup import convert_to_cm

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC05c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([781.6278, 1088.8]))
task_times['phase1'] = nept.Epoch(np.array([1123.0, 1627.4]))
task_times['pauseA'] = nept.Epoch(np.array([1641.9, 2253.5]))
task_times['phase2'] = nept.Epoch(np.array([2301.6, 3516.1]))
task_times['pauseB'] = nept.Epoch(np.array([3575.5, 5383.9]))
task_times['phase3'] = nept.Epoch(np.array([5415.4, 7841.0]))
task_times['postrecord'] = nept.Epoch(np.array([7860.8, 8168.3]))

pxl_to_cm = (7.5269, 6.8437)
scale_targets = (3.7, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [525, 460]
path_pts['turn1'] = [527, 376]
path_pts['pt1'] = [456, 383]
path_pts['pt2'] = [369, 398]
path_pts['pt2a'] = [304, 383]
path_pts['turn2'] = [200, 351]
path_pts['pt3'] = [198, 211]
path_pts['turn3'] = [210, 88]
path_pts['pt4'] = [318, 81]
path_pts['pt5'] = [418, 75]
path_pts['pt6'] = [530, 77]
path_pts['feeder2'] = [629, 82]
path_pts['shortcut1'] = [304, 383]
path_pts['spt1'] = [308, 310]
path_pts['spt2'] = [319, 267]
path_pts['spt3'] = [325, 216]
path_pts['spt4'] = [316, 170]
path_pts['shortcut2'] = [318, 81]
path_pts['novel1'] = [530, 77]
path_pts['npt1'] = [521, 162]
path_pts['npt2'] = [419, 177]
path_pts['novel2'] = [422, 281]
path_pts['pedestal'] = [606, 288]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt2a', 'turn2', 'pt3', 'turn3',
                                           'pt4', 'pt5', 'pt6', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2a', 'turn2', 'pt3', 'turn3', 'pt4', 'pt5', 'pt6']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
