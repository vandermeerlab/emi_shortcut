import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R063d5'
session = 'R063-2015-03-24'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc10a.ncs']
good_swr = [session + '-csc10.mat']
good_theta = [session + '-csc15.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([2160.2, 2479.9]))
task_times['phase1'] = vdm.Epoch(np.array([2516.0, 3119.6]))
task_times['pauseA'] = vdm.Epoch(np.array([3136.2, 3768.3]))
task_times['phase2'] = vdm.Epoch(np.array([3797.6, 5066.1]))
task_times['pauseB'] = vdm.Epoch(np.array([5088.4, 7189.4]))
task_times['phase3'] = vdm.Epoch(np.array([7221.2, 10264.0]))
task_times['postrecord'] = vdm.Epoch(np.array([10285.0, 10591.0]))

pxl_to_cm = (7.4906, 7.2379)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [551, 467]
path_pts['point1'] = [549, 413]
path_pts['point2'] = [538, 380]
path_pts['point3'] = [507, 379]
path_pts['point4'] = [390, 399]
path_pts['point5'] = [258, 375]
path_pts['point6'] = [226, 368]
path_pts['point7'] = [217, 330]
path_pts['point8'] = [220, 235]
path_pts['point9'] = [232, 97]
path_pts['point10'] = [240, 67]
path_pts['point11'] = [277, 51]
path_pts['point12'] = [517, 42]
path_pts['feeder2'] = [658, 66]

path_pts['shortcut1'] = [328, 384]
path_pts['point13'] = [333, 191]
path_pts['point14'] = [350, 158]
path_pts['point15'] = [386, 144]
path_pts['point16'] = [419, 138]
path_pts['point17'] = [441, 141]
path_pts['point18'] = [447, 100]
path_pts['shortcut2'] = [451, 44]

path_pts['novel1'] = [234, 80]
path_pts['point19'] = [152, 79]
path_pts['point20'] = [130, 93]
path_pts['point21'] = [127, 117]
path_pts['novel2'] = [124, 272]
path_pts['pedestal'] = [562, 233]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['point1'], path_pts['point2'],
                path_pts['point3'], path_pts['point4'], path_pts['point5'],
                path_pts['point6'], path_pts['point7'], path_pts['point8'],
                path_pts['point9'], path_pts['point10'], path_pts['point11'],
                path_pts['point12'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['point13'], path_pts['point14'],
                       path_pts['point15'], path_pts['point16'], path_pts['point17'],
                       path_pts['point18'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['point19'], path_pts['point20'],
                    path_pts['point21'], path_pts['novel2']]


sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[10421.9, 10422.4],
                                           [10522.2, 10523.2]]))
sequence['u']['run'] = vdm.Epoch(np.array([[7325, 7350],
                                           [4885, 4915]]))
sequence['u']['ms'] = 7

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[10255.65, 10256.3],
                                                  [9859.7, 9860.5]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[7303, 7333],
                                                  [9165, 9195]]))
sequence['shortcut']['ms'] = 10