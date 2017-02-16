import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R068_EI'
session_id = 'R068d2'
session = 'R068-2014-12-04'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'


task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([762.7549, 1067.1]))
task_times['phase1'] = nept.Epoch(np.array([1110.1, 1600.8]))
task_times['pauseA'] = nept.Epoch(np.array([1662.4, 2266.8]))
task_times['phase2'] = nept.Epoch(np.array([2328.4, 3544.6]))
task_times['pauseB'] = nept.Epoch(np.array([3582.9, 5416.6]))
task_times['phase3'] = nept.Epoch(np.array([5450.7, 8464.4]))
task_times['postrecord'] = nept.Epoch(np.array([8526.8, 8970.9]))

pxl_to_cm = (7.2853, 7.1159)
scale_targets = (3.6, 3.5)

fs = 2000

run_threshold = 0.0

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
path_pts['shortcut1'] = [518, 373]
path_pts['spt1'] = [529, 233]
path_pts['spt2'] = [532, 187]
path_pts['spt3'] = [555, 174]
path_pts['spt4'] = [613, 161]
path_pts['spt5'] = [630, 146]
path_pts['shortcut2'] = [631, 58]
path_pts['novel1'] = [199, 361]
path_pts['npt1'] = [107, 366]
path_pts['npt2'] = [91, 329]
path_pts['novel2'] = [96, 167]
path_pts['pedestal'] = [345, 214]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'turn2',
                                           'pt5', 'turn3', 'pt6', 'pt7', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['turn1', 'pt2', 'pt3', 'pt4', 'turn2',
                                      'pt5', 'turn3', 'pt6', 'pt7', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['run'] = nept.Epoch(np.array([[2458.4, 2498.4]]))

sequence['u']['swr'] = nept.Epoch(np.array([[7721.2, 7721.5]]))
