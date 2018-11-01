import os
import numpy as np
import nept
import info.meta

rat_id = 'R063_EI'
session_id = 'R063d5'
session = 'R063-2015-03-24'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC11a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC12c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(23.393939393939398, 215.3939393939394+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-0.545454545454545, 155.45454545454547+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([2160.3, 2479.9]))
task_times['phase1'] = nept.Epoch(np.array([2516.0, 3119.4]))
task_times['pauseA'] = nept.Epoch(np.array([3136.3, 3768.3]))
task_times['phase2'] = nept.Epoch(np.array([3797.6, 5060.0]))
task_times['pauseB'] = nept.Epoch(np.array([5088.4, 7189.3]))
task_times['phase3'] = nept.Epoch(np.array([7221.2, 10263.9]))
task_times['postrecord'] = nept.Epoch(np.array([10285.4, 10590.3]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [197.6, 17.]
path_pts['pt1'] = [100.5, 14.3]
path_pts['turn1'] = [73., 19.4]
path_pts['pt2'] = [69.2, 51.7]
path_pts['pt3'] = [66., 82.9]
path_pts['turn2'] = [67.4, 105.1]
path_pts['turn3'] = [165., 117.7]
path_pts['feeder2'] = [166.1, 143.]
path_pts['shortcut1'] = [136., 14.3]
path_pts['spt1'] = [133.3, 37.5]
path_pts['spt2'] = [117.1, 44.3]
path_pts['spt3'] = [102.7, 53.1]
path_pts['spt4'] = [99.7, 83.3]
path_pts['shortcut2'] = [98.8, 115.2]
path_pts['novel1'] = [73., 19.4]
path_pts['npt1'] = [38.8, 22.]
path_pts['novel2'] = [35.4, 78.9]
path_pts['pedestal'] = [173.4, 65.8]
path_pts['stable1'] = [131., 119.]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'pt1', 'turn1', 'pt2', 'pt3', 'turn2',
                                      'shortcut2', 'stable1', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'pt2', 'pt3', 'turn2', 'shortcut2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[10421.9, 10422.4],
                                           [10522.2, 10523.2]]))
sequence['u']['run'] = nept.Epoch(np.array([[7325, 7350],
                                           [4885, 4915]]))
sequence['u']['ms'] = 7

sequence['shortcut']['swr'] = nept.Epoch(np.array([[10255.65, 10256.3],
                                                  [9859.7, 9860.5]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[7303, 7333],
                                                  [9165, 9195]]))
sequence['shortcut']['ms'] = 10
