import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d3'
session = 'R068-2014-12-05'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc05c.ncs']
good_swr = [session + '-csc05.mat']
good_theta = [session + '-csc11.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([661.8095, 965.1690]))
task_times['phase1'] = vdm.Epoch(np.array([1039.8, 1665.2]))
task_times['pauseA'] = vdm.Epoch(np.array([1685.3, 2370.1]))
task_times['phase2'] = vdm.Epoch(np.array([2570.9, 3807.9]))
task_times['pauseB'] = vdm.Epoch(np.array([3825.8, 5676.1]))
task_times['phase3'] = vdm.Epoch(np.array([5714.6, 8716.0]))
task_times['postrecord'] = vdm.Epoch(np.array([8741.7, 9083.8]))

pxl_to_cm = (7.2090, 7.0877)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['pt1'] = [524, 409]
path_pts['turn1'] = [518, 373]
path_pts['pt2'] = [423, 381]
path_pts['pt3'] = [362, 394]
path_pts['pt4'] = [274, 374]
path_pts['turn2'] = [199, 361]
path_pts['pt5'] = [202, 162]
path_pts['turn3'] = [207, 58]
path_pts['pt6'] = [302, 46]
path_pts['pt7'] = [422, 49]
path_pts['feeder2'] = [631, 58]
path_pts['shortcut1'] = [424, 381]
path_pts['spt1'] = [423, 309]
path_pts['spt2'] = [435, 285]
path_pts['spt3'] = [469, 274]
path_pts['spt4'] = [607, 271]
path_pts['spt5'] = [630, 261]
path_pts['spt6'] = [641, 214]
path_pts['shortcut2'] = [631, 58]
path_pts['novel1'] = [207, 58]
path_pts['npt1'] = [133, 49]
path_pts['npt2'] = [107, 53]
path_pts['novel2'] = [102, 156]
path_pts['pedestal'] = [328, 182]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]