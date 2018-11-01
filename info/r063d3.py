import os
import numpy as np
import nept
import info.meta

rat_id = 'R063_EI'
session_id = 'R063d3'
session = 'R063-2015-03-22'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC11b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(21.941176470588236, 213.94117647058818+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-1.2941176470588234, 142.7058823529412+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([837.4714, 1142.9]))
task_times['phase1'] = nept.Epoch(np.array([1207.9, 2087.3]))
task_times['pauseA'] = nept.Epoch(np.array([2174.3, 2800.5]))
task_times['phase2'] = nept.Epoch(np.array([2836.3, 4033.9]))
task_times['pauseB'] = nept.Epoch(np.array([4051.3, 6185.3]))
task_times['phase3'] = nept.Epoch(np.array([6249.5, 9373.5]))
task_times['postrecord'] = nept.Epoch(np.array([9395.4, 9792.5]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

track_length = dict()
track_length['u'] = 135.64054453696744
track_length['shortcut'] = 66.21919542141069
track_length['novel'] = 45.19157442807024

path_pts = dict()
path_pts['feeder1'] = [191.2, 17.]
path_pts['turn1'] = [70.8, 20.7]
path_pts['pt1'] = [65.8, 63.1]
path_pts['turn2'] = [66.9, 104.5]
path_pts['pt2'] = [100.3, 117.5]
path_pts['turn3'] = [159.4, 111.3]
path_pts['feeder2'] = [161.2, 138.8]
path_pts['shortcut1'] = [191.2, 17.]
path_pts['spt1'] = [194.2, 56.7]
path_pts['spt2'] = [192.2, 76.9]
path_pts['spt3'] = [159.4, 79.8]
path_pts['spt4'] = [132., 86.2]
path_pts['shortcut2'] = [129.8, 114.]
path_pts['novel1'] = [70.8, 20.7]
path_pts['npt1'] = [38.2, 17.]
path_pts['novel2'] = [38.7, 75.7]
path_pts['pedestal'] = [108.5, 50.4]
path_pts['stable1'] = [124.5, 13.5]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2', 'pt2',
                                      'shortcut2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'pt1', 'turn2', 'pt2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[9692.2, 9692.5],
                                           [9735.65, 9736.1]]))
sequence['u']['run'] = nept.Epoch(np.array([[2950, 2975],
                                           [3285, 3315]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[9692.2, 9692.7],
                                                  [9450.01, 9450.4],
                                                  [9735.75, 9736.1]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[8000, 8030],
                                                  [7950, 7980],
                                                  [8035, 8065]]))
sequence['shortcut']['ms'] = 10
