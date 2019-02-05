import os
import numpy as np
import nept
import info.meta

rat_id = 'R066_EI'
session_id = 'R066d4'
session = 'R066-2014-12-01'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(20.606060606060606, 212.60606060606065+info.meta.binsize, info.meta.binsize)
yedges = np.arange(6.0606060606060606, 150.0606060606061+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([8821.0], [9134.5])
task_times['phase1'] = nept.Epoch([9167.7], [9648.7])
task_times['pauseA'] = nept.Epoch([9772.5], [10373.5])
task_times['phase2'] = nept.Epoch([10405.8], [11605.7])
task_times['pauseB'] = nept.Epoch([11675.0], [13478.8])
task_times['phase3'] = nept.Epoch([13514.5], [15618.4])
task_times['postrecord'] = nept.Epoch([15649.8], [16256.8])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [188.5, 17.]
path_pts['pt1'] = [524, 396]
path_pts['turn1'] = [66., 20.4]
path_pts['pt1'] = [59.3, 45.3]
path_pts['pt2'] = [58.5, 80.8]
path_pts['turn2'] = [61.4, 105.7]
path_pts['pt3'] = [126.2, 115.]
path_pts['turn3'] = [161.4, 114.8]
path_pts['feeder2'] = [158.8, 141.8]
path_pts['shortcut1'] = [188.5, 17.]
path_pts['spt1'] = [193.4, 72.1]
path_pts['spt2'] = [189.4, 108.3]
path_pts['shortcut2'] = [161.4, 114.8]
path_pts['novel1'] = [92., 117.1]
path_pts['npt1'] = [90., 143.3]
path_pts['novel2'] = [23.8, 143.3]
path_pts['pedestal'] = [103., 66.]
path_pts['stable1'] = [125., 12.8]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'pt2', 'turn2', 'novel1', 'pt3',
                                      'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt2', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

# sequence = dict(u=dict(), shortcut=dict())
# sequence['u']['swr'] = nept.Epoch(np.array([[16227.0, 16230.0],
#                                            [15740.45, 15740.6]]))
# sequence['u']['run'] = nept.Epoch(np.array([[9312.7, 9342.7],
#                                            [10766.0, 10796.0]]))
# sequence['u']['ms'] = 10
#
# sequence['shortcut']['swr'] = nept.Epoch(np.array([[15687.0, 15687.55],
#                                                   [15938.9, 15939.3]]))
# sequence['shortcut']['run'] = nept.Epoch(np.array([[13544.0, 13574.0],
#                                                   [14579.0, 14609.0]]))
# sequence['shortcut']['ms'] = 10

lfp_z_thresh = 2.0
