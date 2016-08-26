import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

session_id = 'R066d1'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'


pos_mat = 'R066-2014-11-27-vt.mat'
event_mat = 'R066-2014-11-27-event.mat'
spike_mat = 'R066-2014-11-27-spike.mat'

good_lfp = ['R066-2014-11-27-csc11c.ncs']
good_swr = ['R066-2014-11-27-csc11.mat']
good_theta = ['R066-2014-11-27-csc02.mat']

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([15415.0, 15716.0]))
task_times['phase1'] = vdm.Epoch(np.array([15792.0, 16397.0]))
task_times['pauseA'] = vdm.Epoch(np.array([16465.0, 18860.0]))
task_times['phase2'] = vdm.Epoch(np.array([19589.0, 22292.0]))
task_times['pauseB'] = vdm.Epoch(np.array([22353.0, 24156.0]))
task_times['phase3'] = vdm.Epoch(np.array([24219.0, 26922.0]))
task_times['postrecord'] = vdm.Epoch(np.array([26960, 27263]))

pxl_to_cm = (7.6286, 7.1722)

fs = 2000

run_threshold = 0.0

# Session-specific path trajectory points
path_pts = dict()
path_pts['feeder1'] = [524, 466]
path_pts['pt1'] = [529, 409]
path_pts['turn1'] = [523, 376]
path_pts['pt2'] = [473, 378]
path_pts['pt3'] = [416, 388]
path_pts['pt4'] = [347, 390]
path_pts['pt5'] = [313, 368]
path_pts['pt6'] = [279, 398]
path_pts['pt7'] = [229, 376]
path_pts['pt8'] = [183, 363]
path_pts['pt9'] = [192, 306]
path_pts['pt10'] = [195, 109]
path_pts['turn2'] = [204, 45]
path_pts['pt11'] = [261, 47]
path_pts['pt12'] = [294, 34]
path_pts['pt13'] = [515, 40]
path_pts['pt14'] = [604, 74]
path_pts['feeder2'] = [643, 66]
path_pts['shortcut1'] = [414, 381]
path_pts['spt1'] = [415, 217]
path_pts['shortcut2'] = [416, 48]
path_pts['novel1'] = [204, 168]
path_pts['npt1'] = [111, 163]
path_pts['npt2'] = [95, 185]
path_pts['novel2'] = [90, 370]
path_pts['pedestal'] = [553, 212]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['pt7'],
                path_pts['pt8'], path_pts['pt9'], path_pts['pt10'],
                path_pts['turn2'], path_pts['pt11'], path_pts['pt12'],
                path_pts['pt13'], path_pts['pt14'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[27229.75, 27230],
                                           [27082.1, 27082.5]]))
sequence['u']['run'] = vdm.Epoch(np.array([[20480, 20510],
                                           [20588.5, 20618.5]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[26988.75, 26989],
                                                  [27019, 27019.6]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[24700, 24730],
                                                  [24755, 24785]]))
sequence['shortcut']['ms'] = 10

