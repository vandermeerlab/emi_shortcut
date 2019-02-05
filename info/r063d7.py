import os
import numpy as np
import nept
import info.meta

rat_id = 'R063_EI'
session_id = 'R063d7'
session = 'R063-2015-03-26'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(54.03030303030303, 222.03030303030303+info.meta.binsize, info.meta.binsize)
yedges = np.arange(3.121212121212121, 147.12121212121212+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([3711.6], [4033.0])
task_times['phase1'] = nept.Epoch([4078.4], [4622.6])
task_times['pauseA'] = nept.Epoch([4649.5], [5255.4])
task_times['phase2'] = nept.Epoch([5281.2], [6482.5])
task_times['pauseB'] = nept.Epoch([6497.2], [8414.0])
task_times['phase3'] = nept.Epoch([8441.9], [9943.8])
task_times['postrecord'] = nept.Epoch([9961.5], [10357.0])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.65

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [200.6, 22.4]
path_pts['turn1'] = [75.6, 27.9]
path_pts['pt1'] = [73.7, 67.2]
path_pts['turn2'] = [77.4, 109.4]
path_pts['turn3'] = [173.5, 112.8]
path_pts['feeder2'] = [175.2, 140.6]
path_pts['shortcut1'] = [104., 22.4]
path_pts['spt1'] = [108., 43.]
path_pts['spt2'] = [113., 58.2]
path_pts['spt3'] = [113., 76.7]
path_pts['spt4'] = [107.5, 95.5]
path_pts['shortcut2'] = [107.6, 115.7]
path_pts['novel1'] = [171., 20.6]
path_pts['npt1'] = [171.2, 47.2]
path_pts['npt2'] = [137.2, 49.7]
path_pts['novel2'] = [136.5, 80.3]
path_pts['pedestal'] = [196.3, 79.4]
path_pts['stable1'] = [142.4, 115.5]

u_trajectory = [path_pts[i] for i in ['feeder1', 'novel1', 'shortcut1', 'turn1', 'pt1', 'turn2',
                                      'shortcut2', 'stable1', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['turn1', 'pt1', 'turn2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'novel2']]

# sequence = dict(u=dict(), shortcut=dict())
# sequence['u']['swr'] = nept.Epoch(np.array([[9929, 9933]]))
# sequence['u']['run'] = nept.Epoch(np.array([[9541, 9584]]))
#
# sequence['shortcut']['swr'] = nept.Epoch(np.array([[8894, 8929]]))
# sequence['shortcut']['run'] = nept.Epoch(np.array([[8153, 8156]]))

lfp_z_thresh = 1.5
