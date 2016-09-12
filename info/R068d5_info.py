import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R068d5'
session = 'R068-2014-12-07'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc15c.ncs']
good_swr = [session + '-csc15.mat']
good_theta = [session + '-csc05.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([972.4348, 1282.5]))
task_times['phase1'] = vdm.Epoch(np.array([1318.8, 1938.0]))
task_times['pauseA'] = vdm.Epoch(np.array([1986.8, 2609.1]))
task_times['phase2'] = vdm.Epoch(np.array([2638.1, 3870.7]))
task_times['pauseB'] = vdm.Epoch(np.array([3887.5, 5708.9]))
task_times['phase3'] = vdm.Epoch(np.array([5765.6, 8505.5]))
task_times['postrecord'] = vdm.Epoch(np.array([8545.3, 8887.3]))

pxl_to_cm = (7.2154, 7.1816)

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
path_pts['shortcut1'] = [304, 380]
path_pts['spt1'] = [300, 215]
path_pts['spt2'] = [307, 174]
path_pts['spt3'] = [340, 151]
path_pts['spt4'] = [380, 141]
path_pts['spt5'] = [404, 120]
path_pts['spt6'] = [423, 82]
path_pts['shortcut2'] = [430, 50]
path_pts['novel1'] = [207, 58]
path_pts['npt1'] = [101, 75]
path_pts['novel2'] = [108, 188]
path_pts['pedestal'] = [514, 244]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]
