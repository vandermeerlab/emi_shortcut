import os
import numpy as np
import nept
from utils_maze import convert_to_cm

rat_id = 'R066_EI'
session_id = 'R066d6'
session = 'R066-2014-12-03'

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02b.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC13b.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([22586.0, 22887.0]))
task_times['phase1'] = nept.Epoch(np.array([22920.0, 23533.0]))
task_times['pauseA'] = nept.Epoch(np.array([23573.0, 24175.0]))
task_times['phase2'] = nept.Epoch(np.array([24217.0, 25480.0]))
task_times['pauseB'] = nept.Epoch(np.array([25513.0, 27340.0]))
task_times['phase3'] = nept.Epoch(np.array([27377.0, 30061.0]))
task_times['postrecord'] = nept.Epoch(np.array([30105.0, 30420.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

# pxl_to_cm = (7.1209, 7.1628)
scale_targets = (1.5, 1.5)

fs = 2000

path_pts = dict()
path_pts['feeder1'] = [208, 19]
path_pts['turn1'] = [74, 25]
path_pts['turn2'] = [74, 115]
path_pts['turn3'] = [175, 125]
path_pts['feeder2'] = [175, 155]
path_pts['shortcut1'] = [175, 17.5]
path_pts['spt1'] = [175, 80]
path_pts['spt2'] = [110, 90]
path_pts['shortcut2'] = [100, 125]
path_pts['novel1'] = [74, 115]
path_pts['novel2'] = [65, 160]
path_pts['pedestal'] = [115, 60]
path_pts['stable1'] = [130, 17.5]

u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'turn2', 'turn3', 'feeder2']]
shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'shortcut2']]
novel_trajectory = [path_pts[i] for i in ['novel1', 'novel2']]

default = task_times['postrecord'].start

sequence = dict(u=dict(), shortcut=dict())
sequence['u']['swr'] = nept.Epoch(np.array([[25074, 25077]]))
sequence['u']['run'] = nept.Epoch(np.array([[23100, 23150]]))

sequence['shortcut']['swr'] = nept.Epoch(np.array([[29837, 29840]]))
sequence['shortcut']['run'] = nept.Epoch(np.array([[29046, 29111]]))
