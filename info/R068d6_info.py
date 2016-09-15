import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d6'
session = 'R068-2014-12-08'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc03c.ncs']
good_swr = [session + '-csc03.mat']
good_theta = [session + '-csc15.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1622.4, 1924.0]))
task_times['phase1'] = vdm.Epoch(np.array([1959.6, 2450.4]))
task_times['pauseA'] = vdm.Epoch(np.array([2466.5, 3088.4]))
task_times['phase2'] = vdm.Epoch(np.array([3122.8, 4629.2]))
task_times['pauseB'] = vdm.Epoch(np.array([4657.3, 6482.3]))
task_times['phase3'] = vdm.Epoch(np.array([6524.4, 9277.9]))
task_times['postrecord'] = vdm.Epoch(np.array([9303.1, 9609.8]))

pxl_to_cm = (7.1989, 7.1159)

fs = 2000

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
path_pts['shortcut1'] = [306, 384]
path_pts['spt1'] = [304, 309]
path_pts['spt2'] = [316, 286]
path_pts['spt3'] = [342, 276]
path_pts['spt4'] = [429, 272]
path_pts['spt5'] = [507, 270]
path_pts['spt6'] = [523, 255]
path_pts['spt7'] = [528, 196]
path_pts['shortcut2'] = [525, 54]
path_pts['novel1'] = [199, 361]
path_pts['novel2'] = [194, 476]
path_pts['pedestal'] = [363, 162]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['spt7'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['novel2']]
