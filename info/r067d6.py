import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R067_EI'
session_id = 'R067d6'
session = 'R067-2014-12-05'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC12c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([900.9675, 1203.0]))
task_times['phase1'] = vdm.Epoch(np.array([1252.5, 1761.0]))
task_times['pauseA'] = vdm.Epoch(np.array([1779.0, 2436.1]))
task_times['phase2'] = vdm.Epoch(np.array([2465.9, 3723.5]))
task_times['pauseB'] = vdm.Epoch(np.array([3723.5, 5603.5]))
task_times['phase3'] = vdm.Epoch(np.array([5636.8, 8385.7]))
task_times['postrecord'] = vdm.Epoch(np.array([8412.9, 8716.7]))

pxl_to_cm = (7.4689, 7.2098)
scale_targets = (3.7, 3.8)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [525, 460]
path_pts['turn1'] = [527, 376]
path_pts['pt1'] = [456, 383]
path_pts['pt2'] = [369, 398]
path_pts['turn2'] = [200, 351]
path_pts['pt3'] = [198, 211]
path_pts['turn3'] = [213, 73]
path_pts['pt4'] = [254, 54]
path_pts['pt5'] = [361, 48]
path_pts['pt6'] = [534, 60]
path_pts['feeder2'] = [629, 60]
path_pts['shortcut1'] = [304, 383]
path_pts['spt1'] = [308, 310]
path_pts['spt2'] = [334, 277]
path_pts['spt3'] = [414, 274]
path_pts['spt4'] = [508, 268]
path_pts['spt5'] = [528, 241]
path_pts['spt6'] = [535, 164]
path_pts['shortcut2'] = [534, 60]
path_pts['novel1'] = [200, 351]
path_pts['novel2'] = [193, 473]
path_pts['pedestal'] = [351, 157]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

u_trajectory = [path_pts['feeder1'], path_pts['turn1'], path_pts['pt1'],
                path_pts['pt2'], path_pts['turn2'], path_pts['pt3'], path_pts['turn3'], path_pts['pt4'],
                path_pts['pt5'], path_pts['pt6'], path_pts['feeder2']]

shortcut_trajectory = [path_pts['shortcut1'], path_pts['spt1'], path_pts['spt2'],
                       path_pts['spt3'], path_pts['spt4'], path_pts['spt5'],
                       path_pts['spt6'], path_pts['shortcut2']]

novel_trajectory = [path_pts['novel1'], path_pts['novel2']]
