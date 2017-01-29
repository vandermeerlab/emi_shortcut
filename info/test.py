import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'test_EI'
session_id = 'test'
session = 'test'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'


task_times = dict()
# task_times['prerecord'] = vdm.Epoch(np.array([21296.0, 21598.0]))
task_times['phase1'] = vdm.Epoch(np.array([0., 10.]))
# task_times['pauseA'] = vdm.Epoch(np.array([22271.0, 22875.0]))
task_times['phase2'] = vdm.Epoch(np.array([0., 10.]))
# task_times['pauseB'] = vdm.Epoch(np.array([24194.0, 25997.0]))
task_times['phase3'] = vdm.Epoch(np.array([0., 10.]))
# task_times['postrecord'] = vdm.Epoch(np.array([26960.0, 29393.0]))

pxl_to_cm = (7.1709, 7.0596)
scale_targets = (3.6, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [0, 0]
path_pts['pt1'] = [10, 10]
path_pts['pt2'] = [20, 10]
path_pts['feeder2'] = [100, 100]
path_pts['shortcut1'] = [40, 10]
path_pts['shortcut2'] = [50, 10]
path_pts['novel1'] = [70, 10]
path_pts['novel2'] = [80, 10]
path_pts['pedestal'] = [1, 1]

# path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt1', 'pt2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]

