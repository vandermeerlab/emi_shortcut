import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R063_EI'
session_id = 'R063d6'
session = 'R063-2015-03-25'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC11a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1487.1, 1833.3]))
task_times['phase1'] = vdm.Epoch(np.array([1884.5, 2342.0]))
task_times['pauseA'] = vdm.Epoch(np.array([2357.9, 2965.1]))
task_times['phase2'] = vdm.Epoch(np.array([2995.9, 4046.3]))
task_times['pauseB'] = vdm.Epoch(np.array([4065.9, 6474.4]))
task_times['phase3'] = vdm.Epoch(np.array([6498.2, 9593.5]))
task_times['postrecord'] = vdm.Epoch(np.array([9611.6, 9914.0]))

pxl_to_cm = (7.9773, 7.2098)
scale_targets = (3.9, 3.45)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [551, 465]
path_pts['pt1'] = [553, 420]
path_pts['turn1'] = [540, 378]
path_pts['pt2'] = [509, 379]
path_pts['pt3'] = [438, 394]
path_pts['pt4'] = [391, 409]
path_pts['pt5'] = [327, 382]
path_pts['pt6'] = [325, 397]
path_pts['turn2'] = [228, 352]
path_pts['pt7'] = [222, 328]
path_pts['pt8'] = [221, 221]
path_pts['pt9'] = [221, 111]
path_pts['turn3'] = [225, 65]
path_pts['pt10'] = [274, 54]
path_pts['pt11'] = [477, 44]
path_pts['pt12'] = [560, 52]
path_pts['feeder2'] = [659, 70]
path_pts['shortcut1'] = [327, 382]
path_pts['spt1'] = [325, 333]
path_pts['spt2'] = [346, 281]
path_pts['spt3'] = [384, 272]
path_pts['spt4'] = [521, 267]
path_pts['spt5'] = [551, 260]
path_pts['spt6'] = [561, 237]
path_pts['shortcut2'] = [560, 52]
path_pts['novel1'] = [227, 350]
path_pts['npt1'] = [208, 430]
path_pts['npt2'] = [206, 469]
path_pts['novel2'] = [93, 469]
path_pts['pedestal'] = [380, 156]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'turn2',
                                           'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt5', 'pt6', 'turn2', 'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'spt6', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[9741.2, 9741.4],
                                           [9717, 9717.8]]))
sequence['u']['run'] = vdm.Epoch(np.array([[7155, 7185],
                                           [3042, 3064]]))

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[9276.93, 9277.21],
                                                  [9702, 9702.8]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[6710, 6730],
                                                  [7392, 7422]]))
