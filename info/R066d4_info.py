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
task_times['prerecord'] = vdm.Epoch(np.array([8.8210e+03, 9.1346e+03]))
task_times['phase1'] = vdm.Epoch(np.array([9.1677e+03, 9.6490e+03]))
task_times['pauseA'] = vdm.Epoch(np.array([9.7725e+03, 1.0374e+04]))
task_times['phase2'] = vdm.Epoch(np.array([1.0406e+04, 1.1606e+04]))
task_times['pauseB'] = vdm.Epoch(np.array([1.1675e+04, 1.3479e+04]))
task_times['phase3'] = vdm.Epoch(np.array([1.3514e+04, 1.5619e+04]))
task_times['postrecord'] = vdm.Epoch(np.array([1.5650e+04, 1.6257e+04]))

pxl_to_cm = (7.6032, 7.1722)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [525, 453]
path_pts['point1a'] = [543, 426]
path_pts['point1'] = [533, 400]
path_pts['point2'] = [539, 380]
path_pts['point3'] = [539, 349]
path_pts['point4'] = [491, 372]
path_pts['point5'] = [436, 368]
path_pts['point6'] = [351, 402]
path_pts['point7'] = [314, 371]
path_pts['point8'] = [278, 402]
path_pts['point9'] = [266, 372]
path_pts['point10'] = [218, 374]
path_pts['point11'] = [194, 378]
path_pts['point12'] = [207, 308]
path_pts['point13'] = [197, 82]
path_pts['point14'] = [210, 54]
path_pts['point15'] = [286, 46]
path_pts['point16'] = [520, 44]
path_pts['feeder2'] = [637, 63]
path_pts['shortcut1'] = [566, 373]
path_pts['point17'] = [602, 368]
path_pts['point18'] = [627, 366]
path_pts['point19'] = [636, 330]
path_pts['point20'] = [630, 134]
path_pts['shortcut2'] = [637, 63]
path_pts['novel1'] = [302, 405]
path_pts['point21'] = [303, 455]
path_pts['point22'] = [316, 471]
path_pts['point23'] = [289, 478]
path_pts['novel2'] = [113, 470]
path_pts['pedestal'] = [337, 225]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['point1'], path_pts['point1a'], path_pts['point2'],
                path_pts['point3'], path_pts['point4'], path_pts['point5'],
                path_pts['point6'], path_pts['point7'], path_pts['point8'],
                path_pts['point9'], path_pts['point10'], path_pts['point11'],
                path_pts['point12'], path_pts['point13'], path_pts['point14'],
                path_pts['point15'], path_pts['point16'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['point17'], path_pts['point18'],
                       path_pts['point19'], path_pts['point20'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['point21'], path_pts['point22'],
                    path_pts['point23'], path_pts['novel2']]

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

