import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d5'
session = 'R066-2014-12-02'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc10c.ncs']
good_swr = [session + '-csc10.mat']
good_theta = [session + '-csc07.mat']


task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1.0614e+03, 1.3637e+03]))
task_times['phase1'] = vdm.Epoch(np.array([1.4076e+03, 1.8226e+03]))
task_times['pauseA'] = vdm.Epoch(np.array([1.8522e+03, 2.4569e+03]))
task_times['phase2'] = vdm.Epoch(np.array([2.4925e+03, 3.6944e+03]))
task_times['pauseB'] = vdm.Epoch(np.array([3.7358e+03, 5.5421e+03]))
task_times['phase3'] = vdm.Epoch(np.array([5.5787e+03, 8.5847e+03]))
task_times['postrecord'] = vdm.Epoch(np.array([8.6742e+03, 8.9763e+03]))

pxl_to_cm = (7.2408, 7.1628)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [527, 453]
path_pts['pt1'] = [524, 396]
path_pts['turn1'] = [519, 370]
path_pts['pt2'] = [452, 380]
path_pts['pt3'] = [361, 390]
path_pts['pt4'] = [306, 378]
path_pts['pt5'] = [236, 362]
path_pts['turn2'] = [206, 344]
path_pts['pt6'] = [195, 272]
path_pts['pt7'] = [202, 104]
path_pts['turn3'] = [216, 50]
path_pts['pt8'] = [268, 47]
path_pts['pt9'] = [418, 45]
path_pts['pt10'] = [511, 48]
path_pts['feeder2'] = [607, 55]
path_pts['shortcut1'] = [306, 378]
path_pts['spt1'] = [304, 264]
path_pts['spt2'] = [306, 191]
path_pts['spt3'] = [319, 164]
path_pts['spt4'] = [373, 141]
path_pts['spt5'] = [398, 126]
path_pts['spt6'] = [411, 83]
path_pts['shortcut2'] = [418, 45]
path_pts['novel1'] = [216, 50]
path_pts['npt1'] = [99, 44]
path_pts['novel2'] = [99, 151]
path_pts['pedestal'] = [563, 257]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'], path_pts['pt2'],
                path_pts['pt3'], path_pts['pt4'], path_pts['pt5'], path_pts['turn2'],
                path_pts['pt6'], path_pts['pt7'], path_pts['turn3'], path_pts['pt8'], path_pts['pt9'],
                 path_pts['pt10'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'], path_pts['spt3'],
                       path_pts['spt4'], path_pts['spt5'], path_pts['spt6'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]
