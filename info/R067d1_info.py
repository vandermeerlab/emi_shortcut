import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d1'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = 'R067-2014-11-29-vt.mat'
event_mat = 'R067-2014-11-29-event.mat'
spike_mat = 'R067-2014-11-29-spike.mat'

good_lfp = ['R067-2014-11-29-csc05c.ncs']
good_swr = ['R067-2014-11-29-csc05.mat']
good_theta = ['R067-2014-11-29-csc08.mat']


task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([9479.9, 9783.7]))
task_times['phase1'] = vdm.Epoch(np.array([9858.4, 10463.0]))
task_times['pauseA'] = vdm.Epoch(np.array([1052.7, 11129.0]))
task_times['phase2'] = vdm.Epoch(np.array([11172.0, 12392.0]))
task_times['pauseB'] = vdm.Epoch(np.array([12445.0, 14249.0]))
task_times['phase3'] = vdm.Epoch(np.array([14339.0, 16560.0]))
task_times['postrecord'] = vdm.Epoch(np.array([16631.0, 17041.0]))

pxl_to_cm = (7.3552, 7.1253)

fs = 2000

run_threshold = 0.0

# Session-specific path trajectory points
path_pts = dict()
path_pts['feeder1'] = [524, 466]
path_pts['pt1'] = [529, 409]
path_pts['turn1'] = [529, 366]
path_pts['pt2'] = [471, 373]
path_pts['pt3'] = [416, 379]
path_pts['pt4'] = [342, 394]
path_pts['pt5'] = [287, 382]
path_pts['pt6'] = [238, 367]
path_pts['turn2'] = [194, 354]
path_pts['pt7'] = [199, 172] #
path_pts['turn3'] = [216, 52]
path_pts['pt8'] = [310, 46]
path_pts['pt9'] = [419, 50]
path_pts['pt10'] = [541, 51]
path_pts['feeder2'] = [625, 63]
path_pts['shortcut1'] = [416, 379]
path_pts['spt1'] = [418, 200]
path_pts['shortcut2'] = [419, 50]
path_pts['novel1'] = [199, 172]
path_pts['npt1'] = [107, 165]
path_pts['npt2'] = [96, 187]
path_pts['novel2'] = [91, 372]
path_pts['pedestal'] = [309, 220]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['turn2'],
                path_pts['pt7'], path_pts['turn3'], path_pts['pt8'],
                path_pts['pt9'], path_pts['pt10'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[16744.2, 16745.0]]))
sequence['u']['run'] = vdm.Epoch(np.array([[16056.0, 16100.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[16843.9, 16844.2]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[15529.0, 15573.0]]))
sequence['shortcut']['ms'] = 10
