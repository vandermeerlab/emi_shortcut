import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R063_EI'
session_id = 'R063d7'
session = 'R063-2015-03-26'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC14a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([3711.6, 4033.1]))
task_times['phase1'] = vdm.Epoch(np.array([4078.4, 4622.9]))
task_times['pauseA'] = vdm.Epoch(np.array([4649.5, 5255.4]))
task_times['phase2'] = vdm.Epoch(np.array([5281.2, 6482.6]))
task_times['pauseB'] = vdm.Epoch(np.array([6497.2, 8414.1]))
task_times['phase3'] = vdm.Epoch(np.array([8441.8, 9943.8]))
task_times['postrecord'] = vdm.Epoch(np.array([9961.5, 10357.0]))

pxl_to_cm = (7.2949, 6.8906)
scale_targets = (3.7, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [560, 454]
path_pts['turn1'] = [574, 370]
path_pts['pt1'] = [489, 377]
path_pts['pt2'] = [353, 386]
path_pts['pt3'] = [353, 386]
path_pts['pt4'] = [280, 379]
path_pts['turn2'] = [252, 368]
path_pts['pt5'] = [242, 312]
path_pts['pt6'] = [241, 126]
path_pts['turn3'] = [247, 93]
path_pts['pt7'] = [285, 77]
path_pts['pt8'] = [380, 72]
path_pts['pt9'] = [506, 68]
path_pts['pt10'] = [563, 69]
path_pts['feeder2'] = [647, 78]
path_pts['shortcut1'] = [353, 386]
path_pts['spt1'] = [355, 317]
path_pts['spt2'] = [367, 273]
path_pts['spt3'] = [375, 220]
path_pts['spt4'] = [362, 167]
path_pts['spt5'] = [350, 116]
path_pts['shortcut2'] = [346, 76]
path_pts['novel1'] = [563, 69]
path_pts['npt1'] = [560, 154]
path_pts['npt2'] = [450, 160]
path_pts['novel2'] = [447, 273]
path_pts['pedestal'] = [647, 272]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'pt4', 'turn2', 'pt5', 'pt6',
                                           'turn3', 'pt7', 'pt8', 'pt9', 'pt10', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2', 'pt3', 'pt4', 'turn2', 'pt5', 'pt6',
                                      'turn3', 'pt7', 'pt8', 'pt9', 'pt10']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[9929, 9933]]))
sequence['u']['run'] = vdm.Epoch(np.array([[9541, 9584]]))

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[8894, 8929]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[8153, 8156]]))
