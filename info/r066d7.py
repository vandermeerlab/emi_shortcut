import os
import numpy as np
import vdmlab as vdm
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
task_times['prerecord'] = vdm.Epoch(np.array([939.9331, 1242.0]))
task_times['phase1'] = vdm.Epoch(np.array([1279.1, 1761.1]))
task_times['pauseA'] = vdm.Epoch(np.array([1786.4, 2390.3]))
task_times['phase2'] = vdm.Epoch(np.array([2416.6, 3723.7]))
task_times['pauseB'] = vdm.Epoch(np.array([3741.3, 5565.0]))
task_times['phase3'] = vdm.Epoch(np.array([5636.6, 8682.7]))
task_times['postrecord'] = vdm.Epoch(np.array([8713.1, 9049.3]))

pxl_to_cm = (7.4332, 6.8249)
scale_targets = (3.7, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [524, 453]
path_pts['turn1'] = [523, 389]
path_pts['pt1'] = [429, 384]
path_pts['pt2'] = [325, 390]
path_pts['pt3'] = [251, 369]
path_pts['turn2'] = [201, 350]
path_pts['pt4'] = [193, 285]
path_pts['pt5'] = [202, 134]
path_pts['turn3'] = [215, 94]
path_pts['pt6'] = [247, 77]
path_pts['pt7'] = [315, 77]
path_pts['pt8'] = [356, 72]
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

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'], path_pts['pt2'],
                path_pts['pt3'], path_pts['turn2'], path_pts['pt4'], path_pts['pt5'], path_pts['turn3'],
                path_pts['pt6'], path_pts['pt7'], path_pts['pt8'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'], path_pts['spt3'],
                       path_pts['spt4'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['npt1'], path_pts['npt2'], path_pts['novel2']]

