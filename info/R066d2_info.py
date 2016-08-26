import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d2'
session = 'R066-2014-11-28'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc02c.ncs']
good_swr = [session + '-csc02.mat']
good_theta = [session + '-csc07.mat']


# Experimental session-specific task times for R066 day 2
task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([11850.0, 12155.0]))
task_times['phase1'] = vdm.Epoch(np.array([12210.0, 12840.0]))
task_times['pauseA'] = vdm.Epoch(np.array([12900.0, 13501.0]))
task_times['phase2'] = vdm.Epoch(np.array([13574.0, 14776.0]))
task_times['pauseB'] = vdm.Epoch(np.array([14825.0, 16633.0]))
task_times['phase3'] = vdm.Epoch(np.array([16684.0, 19398.0]))
task_times['postrecord'] = vdm.Epoch(np.array([19436.0, 19742.0]))

pxl_to_cm = (7.5460, 7.2192)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [530, 460]
path_pts['turn1'] = [525, 382]
path_pts['pt1'] = [472, 375]
# path_pts['pt2'] = [425, 397]
# path_pts['pt3'] = [404, 359]
path_pts['pt4'] = [439, 379]
path_pts['pt5'] = [410, 382]
# path_pts['pt6'] = [307, 357]
path_pts['pt7'] = [366, 387]
path_pts['pt8'] = [316, 384]
path_pts['pt9'] = [249, 368]
path_pts['turn2'] = [205, 343]
path_pts['pt10'] = [194, 299]
path_pts['pt11'] = [199, 158]
path_pts['pt12'] = [207, 92]
path_pts['turn3'] = [220, 66]
path_pts['pt13'] = [253, 48]
path_pts['pt14'] = [412, 43]
path_pts['feeder2'] = [623, 54]
# path_pts['pt15'] = [665, 51]
path_pts['shortcut1'] = [525, 382]
path_pts['spt1'] = [528, 220]
path_pts['spt2'] = [540, 181]
path_pts['spt3'] = [568, 168]
path_pts['spt4'] = [614, 153]
path_pts['spt5'] = [630, 119]
path_pts['shortcut2'] = [631, 53]
path_pts['novel1'] = [204, 365]
path_pts['npt1'] = [89, 359]
path_pts['novel2'] = [98, 149]
path_pts['pedestal'] = [331, 206]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'],
                path_pts['pt1'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt7'],
                path_pts['pt8'], path_pts['pt9'], path_pts['turn2'], path_pts['pt10'],
                path_pts['pt11'], path_pts['pt12'], path_pts['turn3'],
                path_pts['pt13'], path_pts['pt14'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[19482.6, 19483.0],
                                           [19613.0, 19613.4],
                                           [19719.95, 19720.5]]))
sequence['u']['run'] = vdm.Epoch(np.array([[19220.0, 19260.0],
                                           [14370.0, 14440.0],
                                           [14130.0, 14160.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[19710.0, 19710.6],
                                                  [16584.8, 16585.2]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[17960.0, 17990.0],
                                                  [18800.0, 18830.0]]))
sequence['shortcut']['ms'] = 10
