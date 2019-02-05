import os
import numpy as np
import nept
import info.meta

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(2.6315789473684212, 194.6315789473684+info.meta.binsize, info.meta.binsize)
yedges = np.arange(4.7368421052631575, 136.73684210526315+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([721.9412], [1027.0])
task_times['phase1'] = nept.Epoch([1075.8], [1569.3])
task_times['pauseA'] = nept.Epoch([1593.9], [2218.9])
task_times['phase2'] = nept.Epoch([2243.4], [3512.4])
task_times['pauseB'] = nept.Epoch([3556.1], [5441.0])
task_times['phase3'] = nept.Epoch([5469.7], [8794.6])
task_times['postrecord'] = nept.Epoch([8812.7], [9143.4])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.9

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [174.2, 15.3]
path_pts['pt1'] = [123.4, 13.7]
path_pts['turn1'] = [40.2, 18.3]
path_pts['pt2'] = [37., 55.5]
path_pts['turn2'] = [38.1, 93.6]
path_pts['pt3'] = [65.7, 102.1]
path_pts['pt4'] = [90.6, 101.9]
path_pts['turn3'] = [122.3, 100.]
path_pts['feeder2'] = [123.1, 123.7]
path_pts['shortcut1'] = [174.2, 15.3]
path_pts['spt1'] = [176., 42.3]
path_pts['spt2'] = [148.8, 44.1]
path_pts['spt3'] = [123.6, 46.3]
path_pts['spt4'] = [122.7, 71.3]
path_pts['shortcut2'] = [122.3, 100.]
path_pts['novel1'] = [38.1, 93.6]
path_pts['novel2'] = [12.7, 92.6]
path_pts['pedestal'] = [78.1, 52.8]
path_pts['stable1'] = [69., 14.2]

u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'stable1', 'turn1', 'pt2', 'turn2',
                                      'pt3', 'pt4', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]

# sequence = dict(u=dict(), shortcut=dict())
# sequence['u']['swr'] = nept.Epoch(np.array([[9133.5, 9134.0],
#                                            [8920.6, 8921.2],
#                                            [9118.6, 9119.4],
#                                            [9120.8, 9121.4]]))
# sequence['u']['run'] = nept.Epoch(np.array([[2593.4, 2633.4],
#                                            [2670.0, 2695.0],
#                                            [2795.0, 2835.0]]))
#
# sequence['shortcut']['swr'] = nept.Epoch(np.array([[9015.0, 9015.5],
#                                                   [8890.85, 8891.35],
#                                                   [9089.1, 9089.9]]))
# sequence['shortcut']['run'] = nept.Epoch(np.array([[8355.0, 8385.0],
#                                                   [8660.0, 8690.0],
#                                                   [8450.0, 8490.0]]))

lfp_z_thresh = 1.5
