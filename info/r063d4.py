import os
import numpy as np
import nept
from startup import convert_to_cm

rat_id = 'R063_EI'
session_id = 'R063d4'
session = 'R063-2015-03-23'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC04a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([1074.6, 1378.7]))
task_times['phase1'] = nept.Epoch(np.array([1415.9, 1847.2]))
task_times['pauseA'] = nept.Epoch(np.array([1860.6, 2486.0]))
task_times['phase2'] = nept.Epoch(np.array([2504.6, 3704.5]))
task_times['pauseB'] = nept.Epoch(np.array([3725.3, 5600.7]))
task_times['phase3'] = nept.Epoch(np.array([5627.4, 8638.8]))
task_times['postrecord'] = nept.Epoch(np.array([8656.4, 9000.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.9628, 7.2755)
scale_targets = (3.9, 3.6)

fs = 2000

run_threshold = 0

path_pts = dict()
path_pts['feeder1'] = [552, 461]
path_pts['pt1'] = [551, 409]
path_pts['turn1'] = [547, 388]
path_pts['pt2'] = [535, 383]
path_pts['pt3'] = [479, 381]
path_pts['pt4'] = [370, 400]
path_pts['pt5'] = [274, 384]
path_pts['turn2'] = [230, 370]
path_pts['pt6'] = [219, 325]
path_pts['pt7'] = [234, 98]
path_pts['turn3'] = [244, 66]
path_pts['pt8'] = [275, 51]
path_pts['pt9'] = [334, 46]
path_pts['feeder2'] = [662, 55]
path_pts['shortcut1'] = [546, 387]
path_pts['spt1'] = [620, 373]
path_pts['spt2'] = [652, 358]
path_pts['spt3'] = [662, 313]
path_pts['spt4'] = [661, 150]
path_pts['shortcut2'] = [662, 55]
path_pts['novel1'] = [331, 392]
path_pts['npt1'] = [324, 460]
path_pts['npt2'] = [316, 471]
path_pts['npt3'] = [289, 478]
path_pts['novel2'] = [113, 470]
path_pts['pedestal'] = [412, 203]
path_pts['stable1'] = [331, 47]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'turn2', 'pt6',
                                           'pt7', 'turn3', 'pt8', 'pt9', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['turn1', 'pt2', 'pt3', 'pt4', 'pt5', 'turn2', 'pt6',
                                      'pt7', 'turn3', 'pt8', 'pt9', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'npt3', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[8876.4, 8876.7],
                                           [8855.0, 8855.4],
                                           [8965.4, 8966.0]]))
sequence['u']['run'] = nept.Epoch(np.array([[2577, 2607],
                                           [2668.0, 2698.0],
                                           [3632.0, 3667.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[8872.65, 8873.15],
                                                  [8578.9, 8579.5],
                                                  [8575.37, 8575.55],
                                                  [8119.5, 8119.8],
                                                  [8206.82, 8207.38]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[5760.0, 5790.0],
                                                  [6214.0, 6244.0],
                                                  [5900.0, 5945.0],
                                                  [6460.0, 6490.0],
                                                  [6510.0, 6550.0]]))
sequence['shortcut']['ms'] = 10
