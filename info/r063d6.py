import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R063d6'
session = 'R063-2015-03-25'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc11a.ncs']
good_swr = [session + '-csc11.mat']
good_theta = [session + '-csc13.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1487.1, 1833.3]))
task_times['phase1'] = vdm.Epoch(np.array([1884.5, 2342.0]))
task_times['pauseA'] = vdm.Epoch(np.array([2357.9, 2965.1]))
task_times['phase2'] = vdm.Epoch(np.array([2995.9, 4046.3]))
task_times['pauseB'] = vdm.Epoch(np.array([4065.9, 6474.4]))
task_times['phase3'] = vdm.Epoch(np.array([6498.2, 9593.5]))
task_times['postrecord'] = vdm.Epoch(np.array([9611.6, 9914.0]))

pxl_to_cm = (7.9773, 7.2098)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [551, 465]
path_pts['pt1'] = [553, 420]
path_pts['turn1'] = [540, 378]
path_pts['pt2'] = [509, 379]
path_pts['pt3'] = [438, 394]
path_pts['pt4'] = [391, 409]
path_pts['pt5'] = [247, 367]
path_pts['pt6'] = [325, 397]
path_pts['turn2'] = [228, 352]
path_pts['pt7'] = [222, 328]
path_pts['pt8'] = [221, 221]
path_pts['pt9'] = [221, 111]
path_pts['turn3'] = [225, 65]
path_pts['pt10'] = [274, 54]
path_pts['pt11'] = [477, 44]
path_pts['pt12'] = [585, 60]
path_pts['feeder2'] = [659, 70]
path_pts['shortcut1'] = [327, 382]
path_pts['spt1'] = [325, 333]
path_pts['spt2'] = [346, 281]
path_pts['spt3'] = [384, 272]
path_pts['spt4'] = [521, 267]
path_pts['spt5'] = [551, 260]
path_pts['spt6'] = [561, 237]
path_pts['shortcut2'] = [560, 52]
path_pts['novel1'] = [227, 350]
path_pts['npt1'] = [208, 430]
path_pts['npt2'] = [206, 469]
path_pts['novel2'] = [93, 469]
path_pts['pedestal'] = [380, 156]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'], path_pts['pt5'],
                path_pts['pt6'], path_pts['turn2'], path_pts['pt7'],
                path_pts['pt8'], path_pts['pt9'], path_pts['turn3'],
                path_pts['pt10'], path_pts['pt11'], path_pts['pt12'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[9741.2, 9741.4],
                                           [9717, 9717.8]]))
sequence['u']['run'] = vdm.Epoch(np.array([[7155, 7185],
                                           [3042, 3064]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[9276.93, 9277.21],
                                                  [9702, 9702.8]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[6710, 6730],
                                                  [7392, 7422]]))
sequence['shortcut']['ms'] = 10

