import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d2'
session = 'R068-2014-12-04'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc13c.ncs']
good_swr = [session + '-csc13.mat']
good_theta = [session + '-csc02.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([762.7549, 1067.1]))
task_times['phase1'] = vdm.Epoch(np.array([1110.1, 1600.8]))
task_times['pauseA'] = vdm.Epoch(np.array([1662.4, 2266.8]))
task_times['phase2'] = vdm.Epoch(np.array([2328.4, 3544.6]))
task_times['pauseB'] = vdm.Epoch(np.array([3582.9, 5416.6]))
task_times['phase3'] = vdm.Epoch(np.array([5450.7, 8464.4]))
task_times['postrecord'] = vdm.Epoch(np.array([8526.8, 8970.9]))

pxl_to_cm = (7.2853, 7.1159)

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
path_pts['spt1'] = [529, 233]
path_pts['spt2'] = [532, 187]
path_pts['spt3'] = [555, 174]
path_pts['spt4'] = [613, 161]
path_pts['spt5'] = [630, 146]
path_pts['shortcut2'] = [631, 58]
path_pts['novel1'] = [199, 361]
path_pts['npt1'] = [107, 366]
path_pts['npt2'] = [91, 329]
path_pts['novel2'] = [96, 167]
path_pts['pedestal'] = [345, 214]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]
