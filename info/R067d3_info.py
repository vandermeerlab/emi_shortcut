import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d3'
session = 'R067-2014-12-02'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc08d.ncs']
good_swr = [session + '-csc08.mat']
good_theta = [session + '-csc03.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1.4985e+04, 1.5291e+04]))
task_times['phase1'] = vdm.Epoch(np.array([1.5327e+04, 1.5808e+04]))
task_times['pauseA'] = vdm.Epoch(np.array([1.5864e+04, 1.6470e+04]))
task_times['phase2'] = vdm.Epoch(np.array([1.6521e+04, 1.7422e+04]))
task_times['pauseB'] = vdm.Epoch(np.array([1.7460e+04, 1.9270e+04]))
task_times['phase3'] = vdm.Epoch(np.array([1.9314e+04, 2.2017e+04]))
task_times['postrecord'] = vdm.Epoch(np.array([2.2077e+04, 2.2382e+04]))

pxl_to_cm = (7.3680, 7.1535)

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
path_pts['shortcut1'] = [422, 375]
path_pts['spt1'] = [417, 297]
path_pts['spt2'] = [423, 271]
path_pts['spt3'] = [450, 271]
path_pts['spt4'] = [612, 274]
path_pts['spt5'] = [630, 264]
path_pts['spt6'] = [635, 229]
path_pts['shortcut2'] = [629, 60]
path_pts['novel1'] = [205, 58]
path_pts['npt1'] = [119, 50]
path_pts['npt2'] = [97, 61]
path_pts['novel2'] = [95, 160]
path_pts['pedestal'] = [339, 169]

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

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]
