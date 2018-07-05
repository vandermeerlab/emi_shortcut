import os
import numpy as np
import nept

rat_id = 'R067_EI'
session_id = 'R067d3'
session = 'R067-2014-12-02'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC08d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([14985.0, 15291.4]))
task_times['phase1'] = nept.Epoch(np.array([15327.2, 15808.0]))
task_times['pauseA'] = nept.Epoch(np.array([15864.3, 16469.6]))
task_times['phase2'] = nept.Epoch(np.array([16521.0, 17421.5]))
task_times['pauseB'] = nept.Epoch(np.array([17460.5, 19269.8]))
task_times['phase3'] = nept.Epoch(np.array([19314.2, 22016.7]))
task_times['postrecord'] = nept.Epoch(np.array([22077.3, 22382.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [177.7, 16.6]
path_pts['turn1'] = [60.1, 15.4]
path_pts['pt1'] = [56.5, 59.7]
path_pts['turn2'] = [58.4, 99.5]
path_pts['turn3'] = [149.88, 105.3]
path_pts['feeder2'] = [149.7, 133.1]
path_pts['shortcut1'] = [177.7, 16.6]
path_pts['spt1'] = [180.1, 73.6]
path_pts['spt2'] = [147.3, 77.]
path_pts['spt3'] = [121., 80.7]
path_pts['shortcut2'] = [120.8, 106.5]
path_pts['novel1'] = [60.1, 15.4]
path_pts['npt1'] = [28.3, 15.]
path_pts['novel2'] = [27.4, 45.]
path_pts['pedestal'] = [97.8, 46.4]
path_pts['stable1'] = [110.3, 12.7]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2', 'shortcut2', 'turn3', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[21643, 21647]]))
sequence['u']['run'] = nept.Epoch(np.array([[21345, 21377]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[22255, 22257]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[18567, 18607]]))
