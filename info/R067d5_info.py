import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d5'
session = 'R067-2014-12-04'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc07c.ncs']
good_swr = [session + '-csc07.mat']
good_theta = [session + '-csc05.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([12442.0, 12745.0]))
task_times['phase1'] = vdm.Epoch(np.array([12778.0, 13371.0]))
task_times['pauseA'] = vdm.Epoch(np.array([13402.0, 14013.0]))
task_times['phase2'] = vdm.Epoch(np.array([14075.0, 15295.0]))
task_times['pauseB'] = vdm.Epoch(np.array([15331.0, 17132.0]))
task_times['phase3'] = vdm.Epoch(np.array([17170.0, 20303.0]))
task_times['postrecord'] = vdm.Epoch(np.array([20337.0, 20669.0]))

pxl_to_cm = (7.3362, 7.1535)

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
path_pts['shortcut1'] = [304, 379]
path_pts['spt1'] = [304, 222]
path_pts['spt2'] = [310, 179]
path_pts['spt3'] = [326, 152]
path_pts['spt4'] = [350, 145]
path_pts['spt5'] = [392, 144]
path_pts['spt6'] = [407, 131]
path_pts['shortcut2'] = [407, 53]
path_pts['novel1'] = [207, 65]
path_pts['npt1'] = [97, 77]
path_pts['novel2'] = [97, 193]
path_pts['pedestal'] = [540, 248]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['turn2'],
                path_pts['pt7'], path_pts['pt8'], path_pts['pt9'],
                path_pts['turn3'], path_pts['pt10'], path_pts['pt11'],
                path_pts['pt12'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]
