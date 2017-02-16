import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R068_EI'
session_id = 'R068d7'
session = 'R068-2014-12-09'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC03c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([672.6674, 1000.1]))
task_times['phase1'] = nept.Epoch(np.array([1038.0, 1672.9]))
task_times['pauseA'] = nept.Epoch(np.array([1694.4, 2297.5]))
task_times['phase2'] = nept.Epoch(np.array([2325.0, 3591.7]))
task_times['pauseB'] = nept.Epoch(np.array([3643.7, 5479.5]))
task_times['phase3'] = nept.Epoch(np.array([5497.3, 8238.8]))
task_times['postrecord'] = nept.Epoch(np.array([8262.5, 8619.6]))

pxl_to_cm = (7.1911, 6.8155)
scale_targets = (3.6, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 459]
path_pts['turn1'] = [525, 386]
path_pts['pt1'] = [477, 383]
path_pts['pt2'] = [383, 390]
path_pts['pt3'] = [306, 381]
path_pts['turn2'] = [210, 357]
path_pts['pt4'] = [194, 319]
path_pts['pt5'] = [199, 154]
path_pts['turn3'] = [212, 88]
path_pts['pt6'] = [322, 72]
path_pts['pt7'] = [524, 70]
path_pts['feeder2'] = [619, 78]
path_pts['shortcut1'] = [306, 381]
path_pts['spt1'] = [307, 312]
path_pts['spt2'] = [316, 286]
path_pts['spt3'] = [322, 245]
path_pts['spt4'] = [325, 193]
path_pts['spt5'] = [313, 143]
path_pts['shortcut2'] = [322, 72]
path_pts['novel1'] = [524, 70]
path_pts['npt1'] = [517, 154]
path_pts['npt2'] = [415, 159]
path_pts['novel2'] = [414, 273]
path_pts['pedestal'] = [612, 274]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'turn2',
                                           'pt5', 'turn3', 'pt6', 'pt7', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt3', 'pt4', 'turn2', 'pt5', 'turn3', 'pt6', 'pt7']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
