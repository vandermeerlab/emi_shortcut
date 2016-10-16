import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d8'
session = 'R068-2014-12-10'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
# spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc00c.ncs']
good_swr = [session + '-csc00.mat']
good_theta = [session + '-csc00.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([553.1661, 855.2456]))
task_times['phase1'] = vdm.Epoch(np.array([903.6441, 1512.7]))
task_times['pauseA'] = vdm.Epoch(np.array([1607.6, 2291.4]))
task_times['phase2'] = vdm.Epoch(np.array([2333.7, 3555.9]))
task_times['pauseB'] = vdm.Epoch(np.array([3586.1, 5440.8]))
task_times['phase3'] = vdm.Epoch(np.array([5479.6, 8480.2]))
task_times['postrecord'] = vdm.Epoch(np.array([8523.6, 8855.9]))

pxl_to_cm = (7.6141, 6.9188)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['turn1'] = [527, 411]
path_pts['pt1'] = [488, 401]
path_pts['pt2'] = [424, 377]
path_pts['pt3'] = [349, 372]
path_pts['pt4'] = [262, 389]
path_pts['turn2'] = [206, 389]

path_pts['pt5'] = [210, 115]
path_pts['turn3'] = [232, 75]
path_pts['pt6'] = [276, 65]
path_pts['pt7'] = [541, 67]
path_pts['feeder2'] = [632, 72]
path_pts['shortcut1'] = [424, 377]
path_pts['spt1'] = [433, 316]
path_pts['spt2'] = [456, 285]
path_pts['spt3'] = [485, 280]
path_pts['spt4'] = [524, 269]
path_pts['spt5'] = [541, 230]
path_pts['shortcut2'] = [541, 67]
path_pts['novel1'] = [206, 389]
path_pts['npt1'] = [194, 464]
path_pts['novel2'] = [80, 469]
path_pts['pedestal'] = [346, 196]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]