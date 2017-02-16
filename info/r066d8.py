import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d8'
session = 'R066-2014-12-05'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC08c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC05c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([14035.0, 14339.0]))
task_times['phase1'] = nept.Epoch(np.array([14395.0, 14916.0]))
task_times['pauseA'] = nept.Epoch(np.array([14941.0, 15544.0]))
task_times['phase2'] = nept.Epoch(np.array([15586.0, 16833.0]))
task_times['pauseB'] = nept.Epoch(np.array([16910.0, 18739.0]))
task_times['phase3'] = nept.Epoch(np.array([18772.0, 22184.0]))
task_times['postrecord'] = nept.Epoch(np.array([22237.0, 22568.0]))

pxl_to_cm = (7.3552, 7.1628)
scale_targets = (3.7, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [519, 453]
path_pts['turn1'] = [523, 389]
path_pts['pt1'] = [429, 384]
path_pts['pt2'] = [325, 390]
path_pts['pt3'] = [251, 369]
path_pts['turn2'] = [201, 350]
path_pts['pt4'] = [193, 285]
path_pts['pt5'] = [202, 134]
path_pts['turn3'] = [218, 72]
path_pts['pt6'] = [269, 50]
path_pts['pt7'] = [437, 48]
path_pts['pt8'] = [536, 57]
path_pts['feeder2'] = [622, 62]
path_pts['shortcut1'] = [429, 384]
path_pts['spt1'] = [431, 303]
path_pts['spt2'] = [456, 279]
path_pts['spt3'] = [512, 265]
path_pts['spt4'] = [523, 230]
path_pts['spt5'] = [535, 156]
path_pts['shortcut2'] = [536, 57]
path_pts['novel1'] = [201, 350]
path_pts['npt1'] = [195, 459]
path_pts['novel2'] = [92, 461]
path_pts['pedestal'] = [326, 188]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'turn2', 'pt4', 'pt5', 'turn3',
                                           'pt6', 'pt7', 'pt8', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'turn2', 'pt4', 'pt5', 'turn3',
                                      'pt6', 'pt7', 'pt8', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]
