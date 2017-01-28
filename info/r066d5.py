import os
import numpy as np
import vdmlab as vdm
from startup import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d5'
session = 'R066-2014-12-02'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = vdm.Epoch(np.array([1061.4, 1363.7]))
task_times['phase1'] = vdm.Epoch(np.array([1407.6, 1822.6]))
task_times['pauseA'] = vdm.Epoch(np.array([1852.2, 2456.9]))
task_times['phase2'] = vdm.Epoch(np.array([2492.5, 3694.4]))
task_times['pauseB'] = vdm.Epoch(np.array([3735.8, 5542.1]))
task_times['phase3'] = vdm.Epoch(np.array([5578.7, 8584.7]))
task_times['postrecord'] = vdm.Epoch(np.array([8674.2, 8976.3]))

pxl_to_cm = (7.2408, 7.1628)
scale_targets = (3.65, 3.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [527, 453]
path_pts['pt1'] = [524, 396]
path_pts['turn1'] = [519, 370]
path_pts['pt2'] = [452, 380]
path_pts['pt3'] = [361, 390]
path_pts['pt4'] = [306, 378]
path_pts['pt5'] = [236, 362]
path_pts['turn2'] = [206, 344]
path_pts['pt6'] = [195, 272]
path_pts['pt7'] = [202, 104]
path_pts['turn3'] = [216, 50]
path_pts['pt8'] = [268, 47]
path_pts['pt9'] = [418, 45]
path_pts['pt10'] = [511, 48]
path_pts['feeder2'] = [607, 55]
path_pts['shortcut1'] = [306, 378]
path_pts['spt1'] = [304, 264]
path_pts['spt2'] = [306, 191]
path_pts['spt3'] = [319, 164]
path_pts['spt4'] = [373, 141]
path_pts['spt5'] = [398, 126]
path_pts['spt6'] = [411, 83]
path_pts['shortcut2'] = [418, 45]
path_pts['novel1'] = [216, 50]
path_pts['npt1'] = [99, 44]
path_pts['novel2'] = [99, 151]
path_pts['pedestal'] = [563, 257]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'turn2',
                                           'pt6', 'pt7', 'turn3', 'pt8', 'pt9', 'pt10', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt4', 'pt5', 'turn2',
                                      'pt6', 'pt7', 'turn3', 'pt8', 'pt9']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'spt6', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = vdm.Epoch(np.array([[1820, 1823]]))
sequence['u']['run'] = vdm.Epoch(np.array([[1546, 1563]]))

sequence['shortcut']['swr'] = vdm.Epoch(np.array([[7295, 7298]]))
sequence['shortcut']['run'] = vdm.Epoch(np.array([[6680, 6712]]))
