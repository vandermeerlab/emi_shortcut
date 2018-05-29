import os
import numpy as np
import nept
from startup import convert_to_cm

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

lfp_swr_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC02c.ncs')
lfp_theta_filename = os.path.join('data-working', rat_id, session + '_recording', session + '-CSC07c.ncs')

spikes_filepath = os.path.join('data-working', rat_id, session + '_recording')

pickled_events = session + '-event.pkl'
pickled_position = session + '-position.pkl'
pickled_lfp_swr = session + '-lfp_swr.pkl'
pickled_lfp_theta = session + '-lfp_theta.pkl'
pickled_spikes = session + '-spike.pkl'

# Experimental session-specific task times for R066 day 2
task_times = dict()
task_times['prerecord'] = nept.Epoch(np.array([11850.0, 12155.0]))
task_times['phase1'] = nept.Epoch(np.array([12210.0, 12840.0]))
task_times['pauseA'] = nept.Epoch(np.array([12900.0, 13501.0]))
task_times['phase2'] = nept.Epoch(np.array([13574.0, 14776.0]))
task_times['pauseB'] = nept.Epoch(np.array([14825.0, 16633.0]))
task_times['phase3'] = nept.Epoch(np.array([16684.0, 19398.0]))
task_times['postrecord'] = nept.Epoch(np.array([19436.0, 19742.0]))

session_length = 0
for phase in task_times.keys():
    session_length += task_times[phase].durations

pxl_to_cm = (7.5460, 7.2192)
scale_targets = (3.8, 3.5)

fs = 2000

run_threshold = 0.0

path_pts = dict()
path_pts['feeder1'] = [530, 460]
path_pts['turn1'] = [525, 382]
path_pts['pt1'] = [472, 375]
# path_pts['pt2'] = [425, 397]
# path_pts['pt3'] = [404, 359]
path_pts['pt4'] = [439, 379]
path_pts['pt5'] = [410, 382]
# path_pts['pt6'] = [307, 357]
path_pts['pt7'] = [366, 387]
path_pts['pt8'] = [316, 384]
path_pts['pt9'] = [249, 368]
path_pts['turn2'] = [205, 343]
path_pts['pt10'] = [194, 299]
path_pts['pt11'] = [199, 158]
path_pts['pt12'] = [207, 92]
path_pts['turn3'] = [220, 66]
path_pts['pt13'] = [253, 48]
path_pts['pt14'] = [412, 43]
path_pts['feeder2'] = [623, 54]
# path_pts['pt15'] = [665, 51]
path_pts['shortcut1'] = [525, 382]
path_pts['spt1'] = [528, 220]
path_pts['spt2'] = [540, 181]
path_pts['spt3'] = [568, 168]
path_pts['spt4'] = [614, 153]
path_pts['spt5'] = [630, 119]
path_pts['shortcut2'] = [623, 54]
path_pts['novel1'] = [204, 365]
path_pts['npt1'] = [89, 359]
path_pts['novel2'] = [98, 149]
path_pts['pedestal'] = [331, 206]
path_pts['stable1'] = [330, 46]

path_pts = convert_to_cm(path_pts, pxl_to_cm)

full_u_trajectory = [path_pts[i] for i in ['feeder1', 'turn1', 'pt1', 'pt4', 'pt5', 'pt7', 'pt8', 'pt9',
                                           'turn2', 'pt10', 'pt11', 'pt12', 'turn3', 'pt13', 'pt14', 'feeder2']]

u_trajectory = [path_pts[i] for i in ['turn1', 'pt1', 'pt4', 'pt5', 'pt7', 'pt8', 'pt9',
                                      'turn2', 'pt10', 'pt11', 'pt12', 'turn3', 'pt13', 'pt14', 'feeder2']]

shortcut_trajectory = [path_pts[i] for i in ['shortcut1', 'spt1', 'spt2', 'spt3', 'spt4', 'spt5', 'shortcut2']]

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
