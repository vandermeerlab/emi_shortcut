import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d7'
session = 'R067-2014-12-06'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
# event_mat = session + '-event.mat'
# spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc07c.ncs']
good_swr = [session + '-csc07.mat']
good_theta = [session + '-csc05.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([781.6278, 1088.8]))
task_times['phase1'] = vdm.Epoch(np.array([1123.0, 1627.4]))
task_times['pauseA'] = vdm.Epoch(np.array([1641.9, 2253.5]))
task_times['phase2'] = vdm.Epoch(np.array([2301.6, 3516.1]))
task_times['pauseB'] = vdm.Epoch(np.array([3575.5, 5383.9]))
task_times['phase3'] = vdm.Epoch(np.array([5415.4, 7841.0]))
task_times['postrecord'] = vdm.Epoch(np.array([7860.8, 8168.3]))

pxl_to_cm = (7.5269, 6.8437)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [525, 460]
path_pts['turn1'] = [527, 376]
path_pts['pt1'] = [456, 383]
path_pts['pt2'] = [369, 398]
path_pts['turn2'] = [200, 351]
path_pts['pt3'] = [198, 211]
path_pts['turn3'] = [210, 88]
path_pts['pt4'] = [318, 81]
path_pts['pt5'] = [418, 75]
path_pts['pt6'] = [530, 77]
path_pts['feeder2'] = [629, 82]
path_pts['shortcut1'] = [304, 383]
path_pts['spt1'] = [308, 310]
path_pts['spt2'] = [319, 267]
path_pts['spt3'] = [325, 216]
path_pts['spt4'] = [316, 170]
path_pts['shortcut2'] = [318, 81]
path_pts['novel1'] = [530, 77]
path_pts['npt1'] = [521, 162]
path_pts['npt2'] = [419, 177]
path_pts['novel2'] = [422, 281]
path_pts['pedestal'] = [606, 288]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'],
                path_pts['pt2'], path_pts['turn2'], path_pts['pt3'], path_pts['turn3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'], path_pts['novel2']]
