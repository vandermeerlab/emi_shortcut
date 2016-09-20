import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R067d2'
session = 'R067-2014-12-01'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc07d.ncs']
good_swr = [session + '-csc07.mat']
good_theta = [session + '1-csc03.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([33194.0, 33498.0]))
task_times['phase1'] = vdm.Epoch(np.array([33555.0, 34158.0]))
task_times['pauseA'] = vdm.Epoch(np.array([34210.0, 34813.0]))
task_times['phase2'] = vdm.Epoch(np.array([34852.0, 36074.0]))
task_times['pauseB'] = vdm.Epoch(np.array([36142.0, 37955.0]))
task_times['phase3'] = vdm.Epoch(np.array([37993.0, 40759.0]))
task_times['postrecord'] = vdm.Epoch(np.array([40817.0, 41135.0]))

pxl_to_cm = (7.2535, 7.2473)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [527, 460]
path_pts['pt1'] = [527, 415]
path_pts['turn1'] = [525, 374]
path_pts['pt2'] = [461, 377]
path_pts['pt3'] = [385, 388]
path_pts['pt4'] = [328, 394]
path_pts['pt5'] = [303, 388]
path_pts['pt6'] = [221, 370]
path_pts['turn2'] = [199, 356]
path_pts['pt7'] = [192, 323]
path_pts['pt8'] = [193, 209]
path_pts['pt9'] = [203, 89]
path_pts['turn3'] = [207, 65]
path_pts['pt10'] = [231, 56]
path_pts['pt11'] = [322, 43]
path_pts['pt12'] = [512, 46]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [525, 374]
path_pts['spt1'] = [528, 198]
path_pts['spt2'] = [532, 171]
path_pts['spt3'] = [611, 171]
path_pts['spt4'] = [628, 161]
path_pts['shortcut2'] = [629, 60]
path_pts['novel1'] = [199, 356]
path_pts['npt1'] = [93, 358]
path_pts['npt2'] = [94, 322]
path_pts['novel2'] = [107, 157]
path_pts['pedestal'] = [366, 194]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['turn2'],
                path_pts['pt7'], path_pts['pt8'], path_pts['pt9'],
                path_pts['turn3'], path_pts['pt10'], path_pts['pt11'],
                path_pts['pt12'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]

