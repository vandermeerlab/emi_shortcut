import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R067_EI'
session_id = 'R067d4'
session = 'R067-2014-12-03'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([9699.9, 10055.0]))
task_times['phase1'] = vdm.Epoch(np.array([10131.0, 10619.0]))
task_times['pauseA'] = vdm.Epoch(np.array([10683.0, 11289.0]))
task_times['phase2'] = vdm.Epoch(np.array([11337.0, 12570.0]))
task_times['pauseB'] = vdm.Epoch(np.array([12601.0, 14423.0]))
task_times['phase3'] = vdm.Epoch(np.array([14457.0, 17018.0]))
task_times['postrecord'] = vdm.Epoch(np.array([17065.0, 17411.0]))

pxl_to_cm = (7.7049, 7.1347)
scale_targets = (3.8, 3.5)

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
path_pts['pt6'] = [221, 360]
path_pts['turn2'] = [199, 356]
path_pts['pt7'] = [197, 323]
path_pts['pt8'] = [199, 209]
path_pts['pt9'] = [206, 89]
path_pts['turn3'] = [207, 65]
path_pts['pt10'] = [231, 56]
path_pts['pt11'] = [322, 43]
path_pts['pt12'] = [512, 46]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [525, 374]
path_pts['spt1'] = [603, 366]
path_pts['spt2'] = [640, 362]
path_pts['spt3'] = [640, 319]
path_pts['spt4'] = [638, 152]
path_pts['shortcut2'] = [629, 60]
path_pts['novel1'] = [306, 389]
path_pts['npt1'] = [303, 473]
path_pts['novel2'] = [79, 468]
path_pts['pedestal'] = [413, 226]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'turn2',
                                           'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'turn2',
                                      'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[10964, 10966]]))
sequence['u']['run'] = vdm.Epoch(np.array([[11490, 11532]]))

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[17187, 17190]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[14538, 14556]]))
