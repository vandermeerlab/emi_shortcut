import os
import numpy as np
import nept
import info.meta

rat_id = 'R066_EI'
session_id = 'R066d1'
session = 'R066-2014-11-27'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07d.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(10.117647058823529, 214.11764705882354+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-2.8235294117647056, 141.1764705882353+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([15414.7, 15716.4]))
task_times['phase1'] = nept.Epoch(np.array([15792.2, 16396.4]))
task_times['pauseA'] = nept.Epoch(np.array([16464.7, 19549.0]))
task_times['phase2'] = nept.Epoch(np.array([20198.0, 22292.0]))
task_times['pauseB'] = nept.Epoch(np.array([22352.8, 24155.6]))
task_times['phase3'] = nept.Epoch(np.array([24219.0, 26921.6]))
task_times['postrecord'] = nept.Epoch(np.array([26960.5, 27263.2]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [182.9, 16.5]
path_pts['turn1'] = [62., 16.1]
path_pts['turn2'] = [58.2, 104.6]
path_pts['turn3'] = [154.7, 111.6]
path_pts['feeder2'] = [152.9, 138.8]
path_pts['shortcut1'] = [122.8, 14.5]
path_pts['spt1'] = [122.9, 63.9]
path_pts['shortcut2'] = [123.5, 109.7]
path_pts['novel1'] = [57.9, 49.3]
path_pts['npt1'] = [27.7, 48.]
path_pts['novel2'] = [24., 106.8]
path_pts['pedestal'] = [165.3, 61.5]
path_pts['stable1'] = [82.8, 111.]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'novel1', 'turn2', 'stable1',
                                      'shortcut2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['shortcut1', 'turn1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[27229.75, 27230],
                                           [27082.1, 27082.5]]))
sequence['u']['run'] = nept.Epoch(np.array([[20480, 20510],
                                           [20588.5, 20618.5]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[26988.75, 26989],
                                                  [27019, 27019.6]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[24700, 24730],
                                                  [24755, 24785]]))
sequence['shortcut']['ms'] = 10

