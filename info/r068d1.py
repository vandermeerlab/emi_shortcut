import os
import numpy as np
import nept
import info.meta

rat_id = 'R068_EI'
session_id = 'R068d1'
session = 'R068-2014-12-01'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC03a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

xedges = np.arange(5.571428571428571, 197.57142857142856+info.meta.binsize, info.meta.binsize)
yedges = np.arange(-4.714285714285714, 139.28571428571428+info.meta.binsize, info.meta.binsize)

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch([21296.7], [21598.2])
task_times['phase1'] = nept.Epoch([21630.7], [22247.7])
task_times['pauseA'] = nept.Epoch([22270.8], [22874.7])
task_times['phase2'] = nept.Epoch([22910.7], [24131.2])
task_times['pauseB'] = nept.Epoch([24193.6], [25996.8])
task_times['phase3'] = nept.Epoch([26027.3], [29031.3])
task_times['postrecord'] = nept.Epoch([29065.4], [29392.6])

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

scale_targets = 1.75

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [177.7, 16.]
path_pts['turn1'] = [60., 14.3]
path_pts['turn2'] = [57.2, 105.]
path_pts['turn3'] = [149.7, 105.4]
path_pts['feeder2'] = [149.7, 133.7]
path_pts['shortcut1'] = [119.4, 14.]
path_pts['spt1'] = [119., 61.]
path_pts['shortcut2'] = [121.9, 106.7]
path_pts['novel1'] = [56.8, 48.]
path_pts['npt1'] = [27.7, 47.6]
path_pts['novel2'] = [26.5, 103.]
path_pts['pedestal'] = [91.6, 58.5]
path_pts['stable1'] = [88.7, 110.3]

u_trajectory = [path_pts[i] for i in ['feeder1', 'shortcut1', 'turn1', 'novel1', 'turn2',
                                      'stable1', 'shortcut2', 'turn3', 'feeder2']]

u_segment = [path_pts[i] for i in ['shortcut1', 'turn1']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'novel2']]

# sequence = dict(u=dict(), shortcut=dict())
# sequence['u']['swr'] = nept.Epoch(np.array([[27167.0, 27168.1],
#                                            [25070.8, 25072.47]]))
# sequence['u']['run'] = nept.Epoch(np.array([[23873, 23948.85],
#                                            [23237.6, 23349.7]]))
# sequence['u']['ms'] = 12
#
# sequence['shortcut']['swr'] = nept.Epoch(np.array([[27524.2, 27524.9],
#                                                   [27635.15, 27635.85]]))
# sequence['shortcut']['run'] = nept.Epoch(np.array([[27025, 27065],
#                                                   [27185.8, 27231.6]]))
# sequence['shortcut']['ms'] = 13

lfp_z_thresh = 2.0
