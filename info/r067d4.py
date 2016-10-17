import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d4'
session = 'R067-2014-12-03'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc02d.ncs']
good_swr = [session + '-csc02.mat']
good_theta = [session + '-csc13.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([9699.9, 10055.0]))
task_times['phase1'] = vdm.Epoch(np.array([10131.0, 10619.0]))
task_times['pauseA'] = vdm.Epoch(np.array([10683.0, 11289.0]))
task_times['phase2'] = vdm.Epoch(np.array([11337.0, 12570.0]))
task_times['pauseB'] = vdm.Epoch(np.array([12601.0, 14423.0]))
task_times['phase3'] = vdm.Epoch(np.array([14457.0, 17018.0]))
task_times['postrecord'] = vdm.Epoch(np.array([17065.0, 17411.0]))

pxl_to_cm = (7.7049, 7.1347)

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

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['turn2'],
                path_pts['pt7'], path_pts['pt8'], path_pts['pt9'],
                path_pts['turn3'], path_pts['pt10'], path_pts['pt11'],
                path_pts['pt12'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]