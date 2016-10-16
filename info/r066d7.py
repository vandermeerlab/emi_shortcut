import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d7'
session = 'R066-2014-12-04'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

pos_mat = session + '-vt.mat'
event_mat = session + '-event.mat'
# spike_mat = session + '-spike.mat'

good_lfp = [session + '-csc02c.ncs']
good_swr = [session + '-csc02.mat']
good_theta = [session + '-csc07.mat']


task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([939.9331, 1242.0]))
task_times['phase1'] = vdm.Epoch(np.array([1279.1, 1761.1]))
task_times['pauseA'] = vdm.Epoch(np.array([1786.4, 2390.3]))
task_times['phase2'] = vdm.Epoch(np.array([2416.6, 3723.7]))
task_times['pauseB'] = vdm.Epoch(np.array([3741.3, 5565.0]))
task_times['phase3'] = vdm.Epoch(np.array([5636.6, 8682.7]))
task_times['postrecord'] = vdm.Epoch(np.array([8713.1, 9049.3]))

pxl_to_cm = (7.4332, 6.8249)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 453]
path_pts['turn1'] = [523, 389]
path_pts['pt1'] = [429, 384]
path_pts['pt2'] = [325, 390]
path_pts['pt3'] = [251, 369]
path_pts['turn2'] = [201, 350]
path_pts['pt4'] = [193, 285]
path_pts['pt5'] = [202, 134]
path_pts['turn3'] = [215, 94]
path_pts['pt6'] = [247, 77]
path_pts['pt7'] = [315, 77]
path_pts['pt8'] = [356, 72]
path_pts['feeder2'] = [632, 77]
path_pts['shortcut1'] = [308, 382]
path_pts['spt1'] = [312, 306]
path_pts['spt2'] = [325, 249]
path_pts['spt3'] = [327, 210]
path_pts['spt4'] = [318, 146]
path_pts['shortcut2'] = [315, 77]
path_pts['novel1'] = [536, 71]
path_pts['npt1'] = [522, 146]
path_pts['npt2'] = [422, 175]
path_pts['novel2'] = [421, 274]
path_pts['pedestal'] = [603, 270]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'], path_pts['pt2'],
                path_pts['pt3'], path_pts['turn2'], path_pts['pt4'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['pt8'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'], path_pts['spt3'],
                       path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'], path_pts['novel2']]

