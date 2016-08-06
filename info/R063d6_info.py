import os

from startup import load_csc, load_videotrack, load_events, load_spikes, convert_to_cm

session_id = 'R063d6'

thisdir = os.path.dirname(os.path.realpath(__file__))
dataloc = os.path.abspath(os.path.join(thisdir, '..', 'cache', 'data'))

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'


def get_csc():
    return load_csc(os.path.join(dataloc, 'R063-2015-03-25-csc.mat'))


def get_pos(pxl_to_cm):
    pos = load_videotrack(os.path.join(dataloc, 'R063-2015-03-25-vt.mat'))
    pos['x'] = pos['x'] / pxl_to_cm[0]
    pos['y'] = pos['y'] / pxl_to_cm[1]
    return pos


def get_events():
    return load_events(os.path.join(dataloc, 'R063-2015-03-25-event.mat'))


def get_spikes():
    return load_spikes(os.path.join(dataloc, 'R063-2015-03-25-spike.mat'))

# Experimental session-specific task times for R063 day 6
task_times = dict()
task_times['prerecord'] = [1487.1, 1833.3]
task_times['phase1'] = [1884.5, 2342.0]
task_times['pauseA'] = [2357.9, 2965.1]
task_times['phase2'] = [2995.9, 4046.3]
task_times['pauseB'] = [4065.9, 6474.4]
task_times['phase3'] = [6498.2, 9593.5]
task_times['postrecord'] = [9611.6, 9914.0]

pxl_to_cm = (7.9773, 7.2098)

fs = 2000

good_lfp = ['R063-2015-03-25-CSC13d.ncs']
good_swr = ['']
good_theta = ['']

# Session-specific path trajectory points
path_pts = dict()
path_pts['feeder1'] = [551, 465]
path_pts['point1'] = [553, 420]
path_pts['point2'] = [540, 378]
path_pts['point3'] = [533, 381]
path_pts['point4'] = [438, 394]
path_pts['point4a'] = [391, 409]
path_pts['point5'] = [247, 367]
path_pts['point6'] = [325, 397]
path_pts['point7'] = [228, 352]
path_pts['point8'] = [222, 328]
path_pts['point9'] = [221, 221]
path_pts['point10'] = [221, 111]
path_pts['point11'] = [225, 65]
path_pts['point12'] = [274, 54]
path_pts['point13'] = [477, 44]
path_pts['point13a'] = [585, 60]
path_pts['feeder2'] = [648, 67]
path_pts['shortcut1'] = [327, 382]
path_pts['point14'] = [319, 307]
path_pts['point15'] = [346, 281]
path_pts['point16'] = [384, 272]
path_pts['point17'] = [521, 267]
path_pts['point18'] = [551, 260]
path_pts['point19'] = [561, 237]
path_pts['shortcut2'] = [560, 52]
path_pts['novel1'] = [227, 350]
path_pts['point20'] = [208, 430]
path_pts['point21'] = [206, 469]
path_pts['novel2'] = [93, 469]
path_pts['pedestal'] = [380, 156]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['point1'], path_pts['point2'],
                path_pts['point3'], path_pts['point4'], path_pts['point4a'], path_pts['point5'],
                path_pts['point6'], path_pts['point7'], path_pts['point8'],
                path_pts['point9'], path_pts['point10'], path_pts['point11'],
                path_pts['point12'], path_pts['point13'], path_pts['point13a'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['point14'], path_pts['point15'],
                       path_pts['point16'], path_pts['point17'], path_pts['point18'],
                       path_pts['point19'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['point20'], path_pts['point21'],
                    path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr_start'] = [9741.2, 9717]
sequence['u']['swr_stop'] = [9741.4, 9717.8]
sequence['u']['run_start'] = [7155, 3042]
sequence['u']['run_stop'] = [7185, 3064]
sequence['u']['ms'] = 10
sequence['u']['loc'] = 2
sequence['u']['colours'] = ['#bd0026', '#fc4e2a', '#ef3b2c', '#ec7014', '#fe9929',
                            '#78c679', '#41ab5d', '#238443', '#66c2a4', '#41b6c4',
                            '#1d91c0', '#8c6bb1', '#225ea8', '#88419d', '#ae017e',
                            '#dd3497', '#f768a1', '#fcbba1']

sequence['shortcut']['swr_start'] = [9276.93, 9702]
sequence['shortcut']['swr_stop'] = [9277.21, 9702.8]
sequence['shortcut']['run_start'] = [6710, 7392]
sequence['shortcut']['run_stop'] = [6730, 7422]
sequence['shortcut']['ms'] = 10
sequence['shortcut']['loc'] = 2
sequence['shortcut']['colours'] = ['#bd0026', '#fc4e2a', '#ef3b2c', '#ec7014', '#fe9929',
                                   '#78c679', '#41ab5d', '#238443', '#66c2a4', '#41b6c4',
                                   '#1d91c0', '#8c6bb1', '#225ea8', '#88419d', '#ae017e',
                                   '#dd3497', '#f768a1', '#fcbba1', '#fc9272', '#fb6a4a',
                                   '#e31a1c', '#fb6a4a', '#993404', '#b30000', '#800026']

