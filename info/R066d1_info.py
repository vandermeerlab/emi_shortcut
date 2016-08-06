import os

from startup import load_csc, load_videotrack, load_events, load_spikes, convert_to_cm

session_id = 'R066d1'

thisdir = os.path.dirname(os.path.realpath(__file__))
dataloc = os.path.abspath(os.path.join(thisdir, '..', 'cache', 'data'))

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'


def get_csc():
    return load_csc(os.path.join(dataloc, 'R066-2014-11-27-csc.mat'))


def get_pos(pxl_to_cm):
    pos = load_videotrack(os.path.join(dataloc, 'R066-2014-11-27-vt.mat'))
    pos['x'] = pos['x'] / pxl_to_cm[0]
    pos['y'] = pos['y'] / pxl_to_cm[1]
    return pos


def get_events():
    return load_events(os.path.join(dataloc, 'R066-2014-11-27-event.mat'))


def get_spikes():
    return load_spikes(os.path.join(dataloc, 'R066-2014-11-27-spike.mat'))

# Experimental session-specific task times for R066 day 4
task_times = dict()
task_times['prerecord'] = [15415.0, 15716.0]
task_times['phase1'] = [15792.0, 16397.0]
task_times['pauseA'] = [16465.0, 18860.0]
task_times['phase2'] = [19589.0, 22292.0]
task_times['pauseB'] = [22353.0, 24156.0]
task_times['phase3'] = [24219.0, 26922.0]
task_times['postrecord'] = [2.6960, 27263]

pxl_to_cm = (7.6286, 7.1722)

fs = 2000

good_lfp = ['R066-2014-11-27-CSC11d.ncs']
good_swr = ['']
good_theta = ['']

# Session-specific path trajectory points
path_pts = dict()
path_pts['feeder1'] = [522, 466]
path_pts['point1'] = [523, 401]
path_pts['point2'] = [522, 378]
path_pts['point3'] = [493, 385]
path_pts['point4'] = [444, 379]
path_pts['point5'] = [351, 400]
path_pts['point6'] = [335, 402]
path_pts['point7'] = [307, 370]
path_pts['point8'] = [187, 335]
path_pts['point9'] = [274, 406]
path_pts['point10'] = [206, 366]
path_pts['point11'] = [187, 371]
path_pts['point12'] = [190, 335]
path_pts['point13'] = [203, 47]
path_pts['point14'] = [294, 34]
path_pts['point15'] = [515, 40]
path_pts['point15a'] = [604, 74]
path_pts['feeder2'] = [643, 66]
path_pts['shortcut1'] = [414, 381]
path_pts['point17'] = [415, 217]
path_pts['shortcut2'] = [416, 48]
path_pts['novel1'] = [204, 168]
path_pts['point21'] = [111, 163]
path_pts['point22'] = [95, 185]
path_pts['novel2'] = [90, 370]
path_pts['pedestal'] = [553, 212]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['point1'], path_pts['point2'],
                path_pts['point3'], path_pts['point4'], path_pts['point5'],
                path_pts['point6'], path_pts['point7'], path_pts['point8'],
                path_pts['point9'], path_pts['point10'], path_pts['point11'],
                path_pts['point12'], path_pts['point13'], path_pts['point14'],
                path_pts['point15'], path_pts['point15a'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['point17'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['point21'], path_pts['point22'],
                    path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr_start'] = [27229.75, 27082.1]
sequence['u']['swr_stop'] = [27230, 27082.5]
sequence['u']['run_start'] = [20480, 20588.5]
sequence['u']['run_stop'] = [20510, 20618.5]
sequence['u']['ms'] = 10
sequence['u']['loc'] = 2
sequence['u']['colours'] = ['#bd0026', '#fc4e2a', '#ef3b2c', '#ec7014', '#fe9929',
                            '#78c679', '#41ab5d', '#238443', '#66c2a4', '#41b6c4',
                            '#1d91c0', '#8c6bb1', '#225ea8', '#88419d', '#ae017e',
                            '#dd3497', '#f768a1', '#fcbba1', '#fc9272', '#fb6a4a',
                            '#e31a1c', '#fb6a4a', '#993404']

sequence['shortcut']['swr_start'] = [26988.75, 27019]
sequence['shortcut']['swr_stop'] = [26989, 27019.6]
sequence['shortcut']['run_start'] = [24700, 24755]
sequence['shortcut']['run_stop'] = [24730, 24785]
sequence['shortcut']['ms'] = 10
sequence['shortcut']['loc'] = 2
sequence['shortcut']['colours'] = ['#bd0026', '#fc4e2a', '#ef3b2c', '#ec7014', '#fe9929',
                            '#78c679', '#41ab5d', '#238443', '#66c2a4', '#41b6c4',
                            '#1d91c0', '#8c6bb1', '#225ea8', '#88419d', '#ae017e',
                            '#dd3497', '#f768a1', '#fcbba1', '#fc9272', '#fb6a4a',
                            '#e31a1c', '#fb6a4a', '#993404',
                                   '#bd0026', '#fc4e2a', '#ef3b2c', '#ec7014', '#fe9929',
                                   '#78c679', '#41ab5d', '#238443', '#66c2a4', '#41b6c4',
                                   '#1d91c0', '#8c6bb1', '#225ea8', '#88419d', '#ae017e',
                                   '#dd3497', '#f768a1', '#fcbba1', '#fc9272', '#fb6a4a',
                                   '#e31a1c', '#fb6a4a', '#993404'
                                   ]
