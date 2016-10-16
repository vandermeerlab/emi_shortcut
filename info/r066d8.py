import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d8'
session = 'R066-2014-12-05'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
# spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc08c.ncs']
good_swr = [session + '-csc08.mat']
good_theta = [session + '-csc05.mat']


task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([14035.0, 14339.0]))
task_times['phase1'] = vdm.Epoch(np.array([14395.0, 14916.0]))
task_times['pauseA'] = vdm.Epoch(np.array([14941.0, 15544.0]))
task_times['phase2'] = vdm.Epoch(np.array([15586.0, 16833.0]))
task_times['pauseB'] = vdm.Epoch(np.array([16910.0, 18739.0]))
task_times['phase3'] = vdm.Epoch(np.array([18772.0, 22184.0]))
task_times['postrecord'] = vdm.Epoch(np.array([22237.0, 22568.0]))

pxl_to_cm = (7.3552, 7.1628)

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

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'], path_pts['pt2'],
                path_pts['pt3'], path_pts['turn2'], path_pts['pt4'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['pt8'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'], path_pts['spt3'],
                       path_pts['spt4'], path_pts['spt5'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]
