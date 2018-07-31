import os
import numpy as np
import nept
import info.meta

rat_id = 'R066_EI'
session_id = 'R066d3'
session = 'R066-2014-11-29'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC06d.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(14.0, 218.0+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-5.393939393939394, 150.6060606060606+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([20258.1, 20593.0]))
task_times['phase1'] = nept.Epoch(np.array([20688.5, 21165.3]))
task_times['pauseA'] = nept.Epoch(np.array([21217.7, 21827.7]))
task_times['phase2'] = nept.Epoch(np.array([21879.3, 23081.1]))
task_times['pauseB'] = nept.Epoch(np.array([23136.5, 24961.2]))
task_times['phase3'] = nept.Epoch(np.array([25009.9, 27648.9]))
task_times['postrecord'] = nept.Epoch(np.array([27698.4, 28011.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [188.5, 17.]
path_pts['turn1'] = [65.5, 18.5]
path_pts['pt1'] = [60., 64.5]
path_pts['turn2'] = [61.9, 103.5]
path_pts['pt2'] = [94., 115.4]
path_pts['turn3'] = [159., 113.]
path_pts['feeder2'] = [158.8, 141.8]
path_pts['shortcut1'] = [188.5, 17.]
path_pts['spt1'] = [193., 49.3]
path_pts['spt2'] = [191.2, 76.9]
path_pts['spt3'] = [156.6, 80.8]
path_pts['spt4'] = [130., 86.5]
path_pts['shortcut2'] = [128.8, 109.8]
path_pts['novel1'] = [65.5, 18.5]
path_pts['npt1'] = [32.3, 14.7]
path_pts['novel2'] = [30.7, 46.6]
path_pts['pedestal'] = [101.5, 55.]
path_pts['stable1'] = [125.2, 12.5]

u_trajectory = [path_pts[i] for i in ['feeder1', 'stable1', 'turn1', 'pt1', 'turn2', 'pt2',
                                      'shortcut2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'pt1', 'turn2', 'pt2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[27888.2, 27888.6],
                                            [27924.45, 27924.95],
                                            [21466.5, 21466.9]]))
sequence['u']['run'] = nept.Epoch(np.array([[25355, 25385],
                                            [25330, 25360]]))
sequence['u']['ms'] = 15

sequence['shortcut']['swr'] = nept.Epoch(np.array([[27791.2, 27791.8],
                                                   [27833.7, 27834.7],
                                                   [23248.9, 23249.2]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[25170, 25210],
                                                   [25265, 25305]]))
sequence['shortcut']['ms'] = 10
