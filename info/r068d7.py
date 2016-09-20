import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d7'
session = 'R068-2014-12-09'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
# event_mat = session + '-event.mat'
# spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc14c.ncs']
good_swr = [session + '-csc14.mat']
good_theta = [session + '-csc03.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([672.6674, 1000.1]))
task_times['phase1'] = vdm.Epoch(np.array([1038.0, 1672.9]))
task_times['pauseA'] = vdm.Epoch(np.array([1694.4, 2297.5]))
task_times['phase2'] = vdm.Epoch(np.array([2325.0, 3591.7]))
task_times['pauseB'] = vdm.Epoch(np.array([3643.7, 5479.5]))
task_times['phase3'] = vdm.Epoch(np.array([5497.3, 8238.8]))
task_times['postrecord'] = vdm.Epoch(np.array([8262.5, 8619.6]))

pxl_to_cm = (7.1911, 6.8155)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['turn1'] = [525, 386]
path_pts['pt1'] = [477, 383]
path_pts['pt2'] = [383, 390]
path_pts['pt3'] = [306, 381]
path_pts['turn2'] = [210, 357]
path_pts['pt4'] = [194, 319]
path_pts['pt5'] = [199, 154]
path_pts['turn3'] = [212, 88]
path_pts['pt6'] = [322, 72]
path_pts['pt7'] = [524, 70]
path_pts['feeder2'] = [619, 78]
path_pts['shortcut1'] = [306, 381]
path_pts['spt1'] = [307, 312]
path_pts['spt2'] = [316, 286]
path_pts['spt3'] = [322, 245]
path_pts['spt4'] = [325, 193]
path_pts['spt5'] = [313, 143]
path_pts['shortcut2'] = [322, 72]
path_pts['novel1'] = [524, 70]
path_pts['npt1'] = [517, 154]
path_pts['npt2'] = [415, 159]
path_pts['novel2'] = [414, 273]
path_pts['pedestal'] = [612, 274]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'], path_pts['novel2']]
