import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R063_EI'
session_id = 'R063d2'
session = 'R063-2015-03-20'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([721.9412, 1027.1]))
task_times['phase1'] = vdm.Epoch(np.array([1075.8, 1569.6]))
task_times['pauseA'] = vdm.Epoch(np.array([1593.9, 2219.0]))
task_times['phase2'] = vdm.Epoch(np.array([2243.4, 3512.4]))
task_times['pauseB'] = vdm.Epoch(np.array([3556.1, 5441.3]))
task_times['phase3'] = vdm.Epoch(np.array([5469.7, 8794.6]))
task_times['postrecord'] = vdm.Epoch(np.array([8812.7, 9143.4]))

pxl_to_cm = (8.8346, 7.1628)

fs = 2000

track_length = dict()
track_length['u'] = 159.84822710130166
track_length['shortcut'] = 67.52465342828519
track_length['novel'] = 12.337853439884093

path_pts = dict()
path_pts['feeder1'] = [468, 471]
path_pts['pt1'] = [466, 397]
path_pts['turn1'] = [465, 380]
path_pts['pt2'] = [416, 380]
# path_pts['pt3'] = [397, 370]
path_pts['pt4'] = [368, 387]
# path_pts['pt5'] = [337, 376]
path_pts['pt6'] = [293, 400]
path_pts['pt7'] = [173, 367]
path_pts['turn2'] = [148, 359]
path_pts['pt8'] = [138, 319]
path_pts['pt9'] = [140, 103]
path_pts['turn3'] = [155, 69]
path_pts['pt10'] = [203, 58]
path_pts['feeder2'] = [661, 54]
path_pts['shortcut1'] = [467, 378]
path_pts['spt1'] = [465, 175]
path_pts['spt2'] = [500, 164]
path_pts['spt3'] = [645, 164]
path_pts['spt4'] = [669, 162]
path_pts['spt5'] = [672, 146]
path_pts['shortcut2'] = [661, 55]
path_pts['novel1'] = [146, 359]
path_pts['novel2'] = [49, 351]
path_pts['pedestal'] = [295, 200]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['pt1'], path_pts['turn1'],
                path_pts['pt2'], path_pts['pt4'],
                path_pts['pt6'], path_pts['pt7'],
                path_pts['turn2'], path_pts['pt8'], path_pts['pt9'],
                path_pts['turn3'], path_pts['pt10'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[9133.5, 9134.0],
                                           [8920.6, 8921.2],
                                           [9118.6, 9119.4],
                                           [9120.8, 9121.4]]))
sequence['u']['run'] = vdm.Epoch(np.array([[2593.4, 2633.4],
                                           [2670.0, 2695.0],
                                           [2795.0, 2835.0]]))

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[9015.0, 9015.5],
                                                  [8890.85, 8891.35],
                                                  [9089.1, 9089.9]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[8355.0, 8385.0],
                                                  [8660.0, 8690.0],
                                                  [8450.0, 8490.0]]))
