import os
import numpy as np
import nept
import info.meta

rat_id = 'R066_EI'
session_id = 'R066d2'
session = 'R066-2014-11-28'

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
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(13.647058823529413, 205.64705882352942+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-1.3529411764705879, 142.64705882352942+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

# Experimental session-specific task times for R066 day 2
task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([11850.2, 12154.5]))
task_times['phase1'] = nept.Epoch(np.array([12209.6, 12839.8]))
task_times['pauseA'] = nept.Epoch(np.array([12899.5, 13501.3]))
task_times['phase2'] = nept.Epoch(np.array([13573.9, 14776.0]))
task_times['pauseB'] = nept.Epoch(np.array([14825.4, 16632.3]))
task_times['phase3'] = nept.Epoch(np.array([16683.4, 19397.5]))
task_times['postrecord'] = nept.Epoch(np.array([19436.2, 19742.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.7

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [182.9, 15.9]
path_pts['pt1'] = [137.3, 12.1]
path_pts['turn1'] = [63.7, 20.2]
path_pts['pt2'] = [58.3, 57.5]
path_pts['turn2'] = [60.1, 102.1]
path_pts['pt3'] = [103.8, 114.1]
path_pts['turn3'] = [154.2, 109.5]
path_pts['feeder2'] = [156.5, 140.]
path_pts['shortcut1'] = [182.9, 15.9]
path_pts['spt1'] = [183., 43.4]
path_pts['spt2'] = [157.8, 52.9]
path_pts['spt3'] = [154.8, 79.3]
path_pts['shortcut2'] = [154.2, 109.5]
path_pts['novel1'] = [60.1, 102.1]
path_pts['npt1'] = [27.2, 102.5]
path_pts['novel2'] = [29.5, 46.]
path_pts['pedestal'] = [98., 64.3]
path_pts['stable1'] = [97.5, 12.1]

u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'stable1', 'turn1', 'pt2', 'turn2', 'pt3', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['stable1', 'turn1', 'pt2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[19482.6, 19483.0],
                                           [19613.0, 19613.4],
                                           [19719.95, 19720.5]]))
sequence['u']['run'] = nept.Epoch(np.array([[14468.0, 14488.0],
                                           [13826.0, 13866.0],
                                           [14130.0, 14160.0],
                                           [19220.0, 19260.0],
                                           [14370.0, 14440.0]]))
sequence['u']['ms'] = 10

sequence['shortcut']['swr'] = nept.Epoch(np.array([[19370.7, 19371.55],
                                                  [19709.5, 19710.8],
                                                  [16584.8, 16585.2]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[17960.0, 17990.0],
                                                  [18800.0, 18830.0]]))
sequence['shortcut']['ms'] = 10

lfp_z_thresh = 1.5
