import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d4'
session = 'R068-2014-12-06'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc14c.ncs']
good_swr = [session + '-csc14.mat']
good_theta = [session + '-csc10.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1374.3, 1677.4]))
task_times['phase1'] = vdm.Epoch(np.array([1706.3, 2232.6]))
task_times['pauseA'] = vdm.Epoch(np.array([2265.3, 2868.4]))
task_times['phase2'] = vdm.Epoch(np.array([2894.8, 4143.0]))
task_times['pauseB'] = vdm.Epoch(np.array([4167.1, 5995.2]))
task_times['phase3'] = vdm.Epoch(np.array([6033.7, 8743.2]))
task_times['postrecord'] = vdm.Epoch(np.array([8780.8, 9129.5]))

pxl_to_cm = (7.2599, 7.0502)

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
path_pts['shortcut1'] = [518, 373]
path_pts['spt1'] = [601, 378]
path_pts['spt2'] = [630, 373]
path_pts['spt3'] = [641, 349]
path_pts['spt4'] = [643, 228]
path_pts['shortcut2'] = [631, 58]
path_pts['novel1'] = [311, 401]
path_pts['npt1'] = [301, 462]
path_pts['npt2'] = [282, 478]
path_pts['novel2'] = [81, 478]
path_pts['pedestal'] = [372, 216]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]
