from startup import convert_to_cm

session_id = 'R068d1'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'


pos_mat = 'R068-2014-12-01-vt.mat'
event_mat = 'R068-2014-12-01-event.mat'
spike_mat = 'R068-2014-12-01-spike.mat'

good_lfp = ['R068-2014-12-01-csc08c.ncs']
good_swr = ['R068-2014-12-01-csc08.mat']
good_theta = ['R068-2014-12-01-csc02.mat']


task_times = dict()
task_times['prerecord'] = [21296.0, 21598.0]
task_times['phase1'] = [21631.0, 22248.0]
task_times['pauseA'] = [22271.0, 22875.0]
task_times['phase2'] = [22911.0, 24131.0]
task_times['pauseB'] = [24194.0, 25997.0]
task_times['phase3'] = [26027.0, 29031.0]
task_times['postrecord'] = [26960.0, 29393.0]

pxl_to_cm = (7.1709, 7.0596)

fs = 2000

run_threshold = 0.0

# Session-specific path trajectory points
path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['pt1'] = [524, 409]
path_pts['turn1'] = [518, 373]
path_pts['pt2'] = [423, 381]
path_pts['pt3'] = [362, 394]
path_pts['pt4'] = [274, 374]
path_pts['turn2'] = [199, 361]
path_pts['pt5'] = [202, 162]
path_pts['turn3'] = [207, 58]
path_pts['pt6'] = [302, 46]
path_pts['pt7'] = [422, 49]
path_pts['feeder2'] = [631, 58]
path_pts['shortcut1'] = [423, 381]
path_pts['spt1'] = [419, 210]
path_pts['shortcut2'] = [422, 49]
path_pts['novel1'] = [202, 162]
path_pts['npt1'] = [117, 171]
path_pts['npt2'] = [94, 209]
path_pts['novel2'] = [92, 383]
path_pts['pedestal'] = [312, 207]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt3'], path_pts['pt4'],
                path_pts['turn2'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'],
                    path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr_start'] = [27167.0, 25070.8]
sequence['u']['swr_stop'] = [27168.1, 25072.47]
sequence['u']['run_start'] = [23873, 23237.6]
sequence['u']['run_stop'] = [23948.85, 23349.7]
sequence['u']['ms'] = 12

sequence['shortcut']['swr_start'] = [27524.2, 27635.15]
sequence['shortcut']['swr_stop'] = [27524.9, 27635.85]
sequence['shortcut']['run_start'] = [27025, 27185.8]
sequence['shortcut']['run_stop'] = [27065, 27231.6]
sequence['shortcut']['ms'] = 13
