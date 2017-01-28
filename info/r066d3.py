import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d3'
session = 'R066-2014-11-29'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC12c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([20258.0, 20593.0]))
task_times['phase1'] = vdm.Epoch(np.array([20688.0, 21165.0]))
task_times['pauseA'] = vdm.Epoch(np.array([21218.0, 21828.0]))
task_times['phase2'] = vdm.Epoch(np.array([21879.0, 23081.0]))
task_times['pauseB'] = vdm.Epoch(np.array([23136.0, 24962.0]))
task_times['phase3'] = vdm.Epoch(np.array([25009.0, 27649.0]))
task_times['postrecord'] = vdm.Epoch(np.array([27698.0, 28011.0]))

pxl_to_cm = (7.2599, 7.2286)
scale_targets = (3.55, 3.5)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [525, 471]
path_pts['pt1'] = [528, 399]
path_pts['turn1'] = [522, 373]
path_pts['pt2'] = [511, 367]
path_pts['pt3'] = [498, 377]
path_pts['pt4'] = [480, 373]
path_pts['pt5'] = [422, 380]
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

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6', 'pt7', 'pt8',
                                           'turn2', 'pt10', 'pt11', 'turn3', 'pt13', 'pt14', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt5', 'pt6', 'pt7', 'pt8', 'turn2', 'pt10',
                                      'pt11', 'turn3', 'pt13', 'pt14', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4',
                                             'spt5', 'spt6', 'spt7', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'npt3', 'novel2']]

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
