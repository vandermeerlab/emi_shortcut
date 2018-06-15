import os
import numpy as np
import nept
from utils_maze import convert_to_cm

rat_id = 'R067_EI'
session_id = 'R067d3'
session = 'R067-2014-12-02'

species = 'rat'
behavior = 'shortcut'
target = 'dCA1'
experimenter = 'Emily Irvine'

event_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-Events.nev')
event_labels = dict(led1='TTL Output on AcqSystem1_0 board 0 port 2 value (0x0001).',
                    led2='TTL Output on AcqSystem1_0 board 0 port 2 value (0x0002).',
                    ledoff='TTL Output on AcqSystem1_0 board 0 port 2 value (0x0000).',
                    pb1id='TTL Input on AcqSystem1_0 board 0 port 1 value (0x0040).',
                    pb2id='TTL Input on AcqSystem1_0 board 0 port 1 value (0x0020).',
                    pboff='TTL Input on AcqSystem1_0 board 0 port 1 value (0x0000).',
                    feeder1='TTL Output on AcqSystem1_0 board 0 port 0 value (0x0004).',
                    feeder2='TTL Output on AcqSystem1_0 board 0 port 0 value (0x0040).',
                    feederoff='TTL Output on AcqSystem1_0 board 0 port 0 value (0x0000).')

position_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-VT1.nvt')

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC08d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1.4985e+04, 1.5291e+04]))
task_times['phase1'] = nept.Epoch(np.array([1.5327e+04, 1.5808e+04]))
task_times['pauseA'] = nept.Epoch(np.array([1.5864e+04, 1.6470e+04]))
task_times['phase2'] = nept.Epoch(np.array([1.6521e+04, 1.7422e+04]))
task_times['pauseB'] = nept.Epoch(np.array([1.7460e+04, 1.9270e+04]))
task_times['phase3'] = nept.Epoch(np.array([1.9314e+04, 2.2017e+04]))
task_times['postrecord'] = nept.Epoch(np.array([2.2077e+04, 2.2382e+04]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.3680, 7.1535)
scale_targets = (3.7, 3.5)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [527, 460]
path_pts['pt1'] = [527, 415]
path_pts['turn1'] = [525, 374]
path_pts['pt2'] = [422, 377]
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
path_pts['shortcut1'] = [422, 377]
path_pts['spt1'] = [417, 297]
path_pts['spt2'] = [423, 271]
path_pts['spt3'] = [450, 271]
path_pts['spt4'] = [612, 274]
path_pts['spt5'] = [630, 264]
path_pts['spt6'] = [635, 229]
path_pts['shortcut2'] = [629, 60]
path_pts['novel1'] = [207, 65]
path_pts['npt1'] = [119, 50]
path_pts['npt2'] = [97, 61]
path_pts['novel2'] = [95, 160]
path_pts['pedestal'] = [339, 169]
path_pts['stable1'] = [264, 375]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6',
                                           'turn2', 'pt7', 'pt8', 'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'turn2', 'pt7', 'pt8',
                                      'pt9', 'turn3', 'pt10', 'pt11', 'pt12', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'spt6', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[21643, 21647]]))
sequence['u']['run'] = nept.Epoch(np.array([[21345, 21377]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[22255, 22257]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[18567, 18607]]))
