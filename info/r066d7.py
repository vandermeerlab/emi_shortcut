import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d7'
session = 'R066-2014-12-04'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([939.9331, 1242.0]))
task_times['phase1'] = nept.Epoch(np.array([1279.1, 1761.1]))
task_times['pauseA'] = nept.Epoch(np.array([1786.4, 2390.3]))
task_times['phase2'] = nept.Epoch(np.array([2416.6, 3723.7]))
task_times['pauseB'] = nept.Epoch(np.array([3741.3, 5565.0]))
task_times['phase3'] = nept.Epoch(np.array([5636.6, 8682.7]))
task_times['postrecord'] = nept.Epoch(np.array([8713.1, 9049.3]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.4332, 6.8249)
scale_targets = (3.7, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 453]
path_pts['turn1'] = [523, 389]
path_pts['pt1'] = [429, 384]
path_pts['pt2'] = [308, 382]
path_pts['pt3'] = [251, 369]
path_pts['turn2'] = [201, 350]
path_pts['pt4'] = [193, 285]
path_pts['pt5'] = [202, 134]
path_pts['turn3'] = [215, 94]
path_pts['pt6'] = [247, 77]
path_pts['pt7'] = [315, 77]
path_pts['pt8'] = [356, 72]
path_pts['pt9'] = [536, 71]
path_pts['feeder2'] = [632, 77]
path_pts['shortcut1'] = [308, 382]
path_pts['spt1'] = [312, 306]
path_pts['spt2'] = [325, 249]
path_pts['spt3'] = [327, 210]
path_pts['spt4'] = [318, 146]
path_pts['shortcut2'] = [315, 77]
path_pts['novel1'] = [536, 71]
path_pts['npt1'] = [522, 146]
path_pts['npt2'] = [422, 175]
path_pts['novel2'] = [421, 274]
path_pts['pedestal'] = [603, 270]
path_pts['stable1'] = [192, 220]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt2', 'pt3', 'turn2', 'pt4', 'pt5', 'turn3',
                                           'pt6', 'pt7', 'pt8', 'pt9', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt2', 'pt3', 'turn2', 'pt4', 'pt5', 'turn3',
                                      'pt6', 'pt7', 'pt8',  'pt9']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]
