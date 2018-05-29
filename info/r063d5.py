import os
import numpy as np
import nept
from startup import convert_to_cm

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC10a.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC15a.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([2160.2, 2479.9]))
task_times['phase1'] = nept.Epoch(np.array([2516.0, 3119.6]))
task_times['pauseA'] = nept.Epoch(np.array([3136.2, 3768.3]))
task_times['phase2'] = nept.Epoch(np.array([3797.6, 5066.1]))
task_times['pauseB'] = nept.Epoch(np.array([5088.4, 7189.4]))
task_times['phase3'] = nept.Epoch(np.array([7221.2, 10264.0]))
task_times['postrecord'] = nept.Epoch(np.array([10285.0, 10591.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.4906, 7.2379)
scale_targets = (3.7, 3.5)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [551, 467]
path_pts['pt1'] = [549, 413]
path_pts['pt2'] = [538, 380]
path_pts['pt3'] = [507, 379]
path_pts['pt4'] = [390, 399]
path_pts['pt4a'] = [328, 384]
path_pts['pt5'] = [258, 375]
path_pts['pt6'] = [226, 368]
path_pts['pt7'] = [217, 330]
path_pts['pt8'] = [220, 235]
path_pts['pt9'] = [232, 97]
path_pts['pt10'] = [240, 67]
path_pts['pt11'] = [277, 51]
path_pts['pt11a'] = [451, 44]
path_pts['pt12'] = [517, 42]
path_pts['feeder2'] = [658, 66]

path_pts['shortcut1'] = [328, 384]
path_pts['spt1'] = [333, 191]
path_pts['spt2'] = [350, 158]
path_pts['spt3'] = [386, 144]
path_pts['spt4'] = [419, 138]
path_pts['spt5'] = [441, 141]
path_pts['spt6'] = [447, 100]
path_pts['shortcut2'] = [451, 38]

path_pts['novel1'] = [234, 80]
path_pts['npt1'] = [152, 79]
path_pts['npt2'] = [130, 93]
path_pts['npt3'] = [127, 117]
path_pts['novel2'] = [124, 272]
path_pts['pedestal'] = [562, 233]
path_pts['stable1'] = [223, 268]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'pt1', 'pt2', 'pt3', 'pt4', 'pt5', 'pt6',
                                           'pt7', 'pt8', 'pt9', 'pt10', 'pt11', 'pt12', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['pt4a', 'pt5', 'pt6', 'pt7', 'pt8', 'pt9', 'pt10', 'pt11', 'pt11a']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'spt6', 'shortcut2']]

novel_trajectory = [path_pts[i] for i in ['novel1', 'npt1', 'npt2', 'npt3', 'novel2']]

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
