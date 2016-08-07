import os

from startup import load_csc, load_videotrack, load_events, load_spikes, convert_to_cm

session_id = 'R068d1'

thisdir = os.path.dirname(os.path.realpath(__file__))
dataloc = os.path.abspath(os.path.join(thisdir, '..', 'cache', 'data'))

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'


def get_csc(lfp_mat):
    return load_csc(os.path.join(dataloc, lfp_mat))


def get_pos(pxl_to_cm):
    pos = load_videotrack(os.path.join(dataloc, 'R068-2014-12-01-vt.mat'))
    pos['x'] = pos['x'] / pxl_to_cm[0]
    pos['y'] = pos['y'] / pxl_to_cm[1]
    return pos


def get_events():
    return load_events(os.path.join(dataloc, 'R068-2014-12-01-event.mat'))


def get_spikes():
    return load_spikes(os.path.join(dataloc, 'R068-2014-12-01-spike.mat'))

# Experimental session-specific task times for R066 day 4
task_times = dict()
task_times['prerecord'] = [21296.0, 21598.0]
task_times['phase1'] = [21631.0, 22248.0]
task_times['pauseA'] = [22271.0, 22875.0]
task_times['phase2'] = [22911.0, 24131.0]
task_times['pauseB'] = [24194.0, 25997.0]
task_times['phase3'] = [26027.0, 29031.0]
task_times['postrecord'] = [26960.0, 29393.0]

pxl_to_cm = (7.1709, 7.0596)

# import matplotlib.pyplot as plt
# pos = get_pos(pxl_to_cm)
# plt.plot(pos['x'], pos['y'], 'b.')
# plt.show()

fs = 2000

run_threshold = 0.0

good_lfp = ['R068-2014-12-01-CSC08c.ncs']
good_swr = ['R068-2014-12-01-CSC08.mat']
good_theta = ['R068-2014-12-01-CSC02.mat']

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
sequence['u']['swr_start'] = [27635]
sequence['u']['swr_stop'] = [27636]
sequence['u']['run_start'] = [27025]
sequence['u']['run_stop'] = [27080]
sequence['u']['ms'] = 10

sequence['shortcut']['swr_start'] = [27635, 27524]
sequence['shortcut']['swr_stop'] = [27636, 27526]
sequence['shortcut']['run_start'] = [27025]
sequence['shortcut']['run_stop'] = [27080]
sequence['shortcut']['ms'] = 10
