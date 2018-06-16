import os
import numpy as np
import nept

rat_id = 'R067_EI'
session_id = 'R067d4'
session = 'R067-2014-12-03'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC08c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([9699.9, 10055.0]))
task_times['phase1'] = nept.Epoch(np.array([10131.0, 10619.0]))
task_times['pauseA'] = nept.Epoch(np.array([10683.0, 11289.0]))
task_times['phase2'] = nept.Epoch(np.array([11337.0, 12570.0]))
task_times['pauseB'] = nept.Epoch(np.array([12601.0, 14423.0]))
task_times['phase3'] = nept.Epoch(np.array([14457.0, 17018.0]))
task_times['postrecord'] = nept.Epoch(np.array([17065.0, 17411.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [178.3, 16.]
path_pts['turn1'] = [61.8, 18.6]
path_pts['pt1'] = [57.4, 56.5]
path_pts['turn2'] = [58.5, 98.4]
path_pts['pt2'] = [111.5, 110.]
path_pts['turn3'] = [152., 105.5]
path_pts['feeder2'] = [149.7, 133.1]
path_pts['shortcut1'] = [178.3, 16.]
path_pts['spt1'] = [182.8, 66.2]
path_pts['spt2'] = [181., 101.7]
path_pts['shortcut2'] = [152., 105.5]
path_pts['novel1'] = [87.8, 110.2]
path_pts['npt1'] = [87., 135.1]
path_pts['novel2'] = [23.4, 133.7]
path_pts['pedestal'] = [118.4, 64.]
path_pts['pedestal1'] = [92., 56.5]
path_pts['stable1'] = [116.2, 12.8]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2', 'novel1', 'pt2',
                                      'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[10964, 10966]]))
sequence['u']['run'] = nept.Epoch(np.array([[11490, 11532]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[17187, 17190]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[14538, 14556]]))
