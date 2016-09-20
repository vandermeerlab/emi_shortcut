import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d4'
session = 'R066-2014-12-01'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc08c.ncs']
good_swr = [session + '-csc08.mat']
good_theta = [session + '-csc07.mat']


task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([8821.0, 9134.6]))
task_times['phase1'] = vdm.Epoch(np.array([9167.7, 9649.0]))
task_times['pauseA'] = vdm.Epoch(np.array([9772.5, 10374.0]))
task_times['phase2'] = vdm.Epoch(np.array([10406.0, 11606.0]))
task_times['pauseB'] = vdm.Epoch(np.array([11675.0, 13479.0]))
task_times['phase3'] = vdm.Epoch(np.array([13514.0, 15619.0]))
task_times['postrecord'] = vdm.Epoch(np.array([15650.0, 16257.0]))

pxl_to_cm = (7.6032, 7.1722)

fs = 2000

run_threshold = 0.0

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
path_pts['shortcut1'] = [519, 370]
path_pts['spt1'] = [606, 369]
path_pts['spt2'] = [628, 351]
path_pts['spt3'] = [636, 310]
path_pts['spt4'] = [638, 172]
path_pts['shortcut2'] = [607, 55]
path_pts['novel1'] = [306, 378]
path_pts['npt1'] = [290, 472]
path_pts['novel2'] = [85, 473]
path_pts['pedestal'] = [342, 225]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'], path_pts['pt2'],
                path_pts['pt3'], path_pts['pt4'], path_pts['pt5'], path_pts['turn2'],
                path_pts['pt6'], path_pts['pt7'], path_pts['turn3'], path_pts['pt8'], path_pts['pt9'],
                 path_pts['pt10'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'], path_pts['spt3'],
                       path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]


sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[16227.0, 16230.0],
                                           [15740.45, 15740.6]]))
sequence['u']['run'] = vdm.Epoch(np.array([[9312.7, 9342.7],
                                           [10766.0, 10796.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[15687.0, 15687.55],
                                                  [15938.9, 15939.3]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[13544.0, 13574.0],
                                                  [14579.0, 14609.0]]))
sequence['shortcut']['ms'] = 10

