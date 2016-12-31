import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R063_EI'
session_id = 'R063d3'
session = 'R063-2015-03-22'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([837.4714, 1143.1]))
task_times['phase1'] = vdm.Epoch(np.array([1207.9, 2087.5]))
task_times['pauseA'] = vdm.Epoch(np.array([2174.3, 2800.8]))
task_times['phase2'] = vdm.Epoch(np.array([2836.2, 4034.1]))
task_times['pauseB'] = vdm.Epoch(np.array([4051.3, 6185.6]))
task_times['phase3'] = vdm.Epoch(np.array([6249.5, 9373.7]))
task_times['postrecord'] = vdm.Epoch(np.array([9395.4, 9792.5]))

pxl_to_cm = (7.3452, 7.2286)

fs = 2000

track_length = dict()
track_length['u'] = 135.64054453696744
track_length['shortcut'] = 66.21919542141069
track_length['novel'] = 45.19157442807024

path_pts = dict()
path_pts['feeder1'] = [547, 457]
path_pts['point1'] = [558, 451]
path_pts['point2'] = [545, 401]
path_pts['turn1'] = [542, 374]
path_pts['point3'] = [511, 380]
path_pts['point4'] = [443, 399]
path_pts['point5'] = [362, 418]
path_pts['point6a'] = [340, 407]
path_pts['point6'] = [310, 385]
path_pts['point7'] = [292, 404]
path_pts['point8'] = [255, 379]
path_pts['turn2'] = [217, 375]
path_pts['point9'] = [217, 316]
path_pts['point10'] = [236, 84]
path_pts['turn3'] = [249, 59]
path_pts['point11'] = [289, 51]
path_pts['point12'] = [532, 47]
path_pts['feeder2'] = [670, 56]
path_pts['shortcut1'] = [446, 391]
path_pts['spt1'] = [438, 334]
path_pts['spt2'] = [449, 295]
path_pts['spt3'] = [471, 277]
path_pts['spt4'] = [621, 269]
path_pts['spt5'] = [648, 280]
path_pts['spt6'] = [671, 266]
path_pts['spt7'] = [660, 240]
path_pts['shortcut2'] = [654, 56]
path_pts['novel1'] = [247, 61]
path_pts['npt1'] = [146, 53]
path_pts['npt2'] = [132, 83]
path_pts['novel2'] = [130, 266]
path_pts['pedestal'] = [368, 188]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['point1'], path_pts['point2'], path_pts['turn1'],
                path_pts['point3'], path_pts['point4'], path_pts['point5'], path_pts['point6a'], path_pts['point6'],
                path_pts['point7'], path_pts['point8'], path_pts['turn2'], path_pts['point9'],
                path_pts['point10'], path_pts['turn3'], path_pts['point11'], path_pts['point12'],
                path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'], path_pts['spt6'],
                       path_pts['spt7'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'],
                    path_pts['npt2'], path_pts['novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[9692.2, 9692.5],
                                           [9735.65, 9736.1]]))
sequence['u']['run'] = vdm.Epoch(np.array([[2950, 2975],
                                           [3285, 3315]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[9692.2, 9692.7],
                                                  [9450.01, 9450.4],
                                                  [9735.75, 9736.1]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[8000, 8030],
                                                  [7950, 7980],
                                                  [8035, 8065]]))
sequence['shortcut']['ms'] = 10
