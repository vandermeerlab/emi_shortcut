import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d3'
session = 'R066-2014-11-29'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc12c.ncs']
good_swr = [session + '-csc12.mat']
good_theta = [session + '-csc07.mat']


task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([20258.0, 20593.0]))
task_times['phase1'] = vdm.Epoch(np.array([20688.0, 21165.0]))
task_times['pauseA'] = vdm.Epoch(np.array([21218.0, 21828.0]))
task_times['phase2'] = vdm.Epoch(np.array([21879.0, 23081.0]))
task_times['pauseB'] = vdm.Epoch(np.array([23136.0, 24962.0]))
task_times['phase3'] = vdm.Epoch(np.array([25009.0, 27649.0]))
task_times['postrecord'] = vdm.Epoch(np.array([27698.0, 28011.0]))

pxl_to_cm = (7.2599, 7.2286)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [525, 471]
path_pts['pt1'] = [528, 399]
path_pts['turn1'] = [522, 373]
path_pts['pt2'] = [511, 367]
path_pts['pt3'] = [498, 377]
path_pts['pt4'] = [480, 373]
path_pts['pt5'] = [437, 387]
path_pts['pt6'] = [357, 394]
path_pts['pt7'] = [322, 389]
path_pts['pt8'] = [225, 365]
path_pts['turn2'] = [197, 358]
path_pts['pt10'] = [198, 333]
path_pts['pt11'] = [204, 83]
path_pts['turn3'] = [211, 61]
path_pts['pt13'] = [230, 53]
path_pts['pt14'] = [395, 40]
path_pts['feeder2'] = [650, 57]
path_pts['shortcut1'] = [422, 380]
path_pts['spt1'] = [420, 321]
path_pts['spt2'] = [432, 284]
path_pts['spt3'] = [461, 262]
path_pts['spt4'] = [600, 270]
path_pts['spt5'] = [634, 270]
path_pts['spt6'] = [638, 245]
path_pts['spt7'] = [630, 85]
path_pts['shortcut2'] = [650, 57]
path_pts['novel1'] = [211, 61]
path_pts['npt1'] = [162, 37]
path_pts['npt2'] = [124, 43]
path_pts['npt3'] = [107, 75]
path_pts['novel2'] = [104, 156]
path_pts['pedestal'] = [338, 186]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'], path_pts['pt2'],
                path_pts['pt3'], path_pts['pt4'], path_pts['pt5'],
                path_pts['pt6'], path_pts['pt7'], path_pts['pt8'],
                path_pts['turn2'], path_pts['pt10'], path_pts['pt11'],
                path_pts['turn3'], path_pts['pt13'], path_pts['pt14'],
                path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['spt7'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['npt2'], path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[27888.2, 27888.6],
                                           [27924.45, 27924.85]]))
sequence['u']['run'] = vdm.Epoch(np.array([[25360, 25390],
                                           [25320, 25350]]))
sequence['u']['ms'] = 15

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[27791.2, 27791.8],
                                                  [27833.7, 27834.7]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[25170, 25210],
                                                  [25265, 25305]]))
sequence['shortcut']['ms'] = 10