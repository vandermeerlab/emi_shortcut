import os
import numpy as np
import nept
from startup import convert_to_cm

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC03d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([33194.0, 33498.0]))
task_times['phase1'] = nept.Epoch(np.array([33555.0, 34158.0]))
task_times['pauseA'] = nept.Epoch(np.array([34210.0, 34813.0]))
task_times['phase2'] = nept.Epoch(np.array([34852.0, 36074.0]))
task_times['pauseB'] = nept.Epoch(np.array([36142.0, 37955.0]))
task_times['phase3'] = nept.Epoch(np.array([37993.0, 40759.0]))
task_times['postrecord'] = nept.Epoch(np.array([40817.0, 41135.0]))

pxl_to_cm = (7.2535, 7.2473)
scale_targets = (3.6, 3.5)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [527, 460]
path_pts['pt1'] = [527, 415]
path_pts['turn1'] = [525, 374]
path_pts['pt2'] = [461, 377]
path_pts['pt3'] = [385, 388]
path_pts['pt4'] = [328, 394]
path_pts['pt5'] = [303, 388]
path_pts['pt6'] = [221, 370]
path_pts['turn2'] = [199, 356]
path_pts['pt7'] = [192, 323]
path_pts['pt8'] = [193, 209]
path_pts['pt9'] = [203, 89]
path_pts['turn3'] = [207, 65]
path_pts['pt10'] = [231, 56]
path_pts['pt11'] = [322, 43]
path_pts['pt12'] = [512, 46]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [525, 374]
path_pts['spt1'] = [528, 198]
path_pts['spt2'] = [532, 171]
path_pts['spt3'] = [611, 171]
path_pts['spt4'] = [628, 161]
path_pts['shortcut2'] = [629, 60]
path_pts['novel1'] = [199, 356]
path_pts['npt1'] = [93, 358]
path_pts['npt2'] = [94, 322]
path_pts['novel2'] = [107, 157]
path_pts['pedestal'] = [366, 194]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'turn2',
                                           'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'turn2', 'pt7', 'pt8', 'pt9',
                                      'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

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
