import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R063d7'
session = 'R063-2015-03-26'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
# spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc10a.ncs']
good_swr = [session + '-csc10.mat']
good_theta = [session + '-csc14.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([3711.6, 4033.1]))
task_times['phase1'] = vdm.Epoch(np.array([4078.4, 4622.9]))
task_times['pauseA'] = vdm.Epoch(np.array([4649.5, 5255.4]))
task_times['phase2'] = vdm.Epoch(np.array([5281.2, 6482.6]))
task_times['pauseB'] = vdm.Epoch(np.array([6497.2, 8414.1]))
task_times['phase3'] = vdm.Epoch(np.array([8441.8, 9943.8]))
task_times['postrecord'] = vdm.Epoch(np.array([9961.5, 10357.0]))

pxl_to_cm = (7.2949, 6.8906)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [560, 454]
path_pts['turn1'] = [574, 370]
path_pts['pt1'] = [489, 377]
path_pts['pt2'] = [416, 395]
path_pts['pt3'] = [353, 386]
path_pts['pt4'] = [280, 379]
path_pts['turn2'] = [252, 368]
path_pts['pt5'] = [242, 312]
path_pts['pt6'] = [241, 126]
path_pts['turn3'] = [247, 93]
path_pts['pt7'] = [285, 77]
path_pts['pt8'] = [380, 72]
path_pts['pt9'] = [506, 68]
path_pts['pt10'] = [563, 69]
path_pts['feeder2'] = [647, 78]
path_pts['shortcut1'] = [353, 386]
path_pts['spt1'] = [355, 317]
path_pts['spt2'] = [367, 273]
path_pts['spt3'] = [375, 220]
path_pts['spt4'] = [362, 167]
path_pts['spt5'] = [350, 116]
path_pts['shortcut2'] = [346, 76]
path_pts['novel1'] = [563, 69]
path_pts['npt1'] = [560, 154]
path_pts['npt2'] = [450, 160]
path_pts['novel2'] = [447, 273]
path_pts['pedestal'] = [647, 272]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'], path_pts['turn2'],
                path_pts['pt5'], path_pts['pt6'], path_pts['turn3'], path_pts['pt7'],
                path_pts['pt8'], path_pts['pt9'], path_pts['pt10'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                        path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]
