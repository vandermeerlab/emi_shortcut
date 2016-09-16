import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d8'
session = 'R067-2014-12-07'

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
task_times['prerecord'] = vdm.Epoch(np.array([513.2856, 817.4131]))
task_times['phase1'] = vdm.Epoch(np.array([851.5246, 1337.7]))
task_times['pauseA'] = vdm.Epoch(np.array([1359.0, 1961.6]))
task_times['phase2'] = vdm.Epoch(np.array([2007.2, 3209.6]))
task_times['pauseB'] = vdm.Epoch(np.array([3280.4, 5121.1]))
task_times['phase3'] = vdm.Epoch(np.array([5156.7, 8459.1]))
task_times['postrecord'] = vdm.Epoch(np.array([8482.3, 8839.7]))

pxl_to_cm = (7.6795, 7.1253)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [525, 460]
path_pts['turn1'] = [527, 376]
path_pts['pt1'] = [456, 383]
path_pts['pt2'] = [369, 398]
path_pts['turn2'] = [200, 351]
path_pts['pt3'] = [198, 211]
path_pts['turn3'] = [213, 73]
path_pts['pt4'] = [254, 54]
path_pts['pt5'] = [361, 48]
path_pts['pt6'] = [534, 60]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [428, 382]
path_pts['spt1'] = [423, 311]
path_pts['spt2'] = [437, 282]
path_pts['spt3'] = [487, 267]
path_pts['spt4'] = [521, 248]
path_pts['spt5'] = [529, 159]
path_pts['shortcut2'] = [534, 60]
path_pts['novel1'] = [200, 351]
path_pts['npt1'] = [193, 473]
path_pts['novel2'] = [80, 466]
path_pts['pedestal'] = [348, 178]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'],
                path_pts['pt2'], path_pts['turn2'], path_pts['pt3'], path_pts['turn3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]
