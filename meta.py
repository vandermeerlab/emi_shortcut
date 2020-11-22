import numpy as np

_printvals = False
seed = 34

rest_times = ["prerecord", "pauseA", "pauseB", "postrecord"]
run_times = ["phase1", "phase2", "phase3"]
run_times_labels = {
    "phase1": "Phase 1",
    "phase2": "Phase 2",
    "phase3": "Phase 3",
}

task_times = [
    "prerecord",
    "phase1",
    "pauseA",
    "phase2",
    "pauseB",
    "phase3",
    "postrecord",
]
task_times_labels = {
    "prerecord": "Pre-task",
    "phase1": "Phase 1",
    "pauseA": "Pause A",
    "phase2": "Phase 2",
    "pauseB": "Pause B",
    "phase3": "Phase 3",
    "postrecord": "Post-task",
}
phases_corr = ["phases12", "phases13", "phases23"]
phases_corr_labels = {
    "phases12": "Phases 1-2",
    "phases13": "Phases 1-3",
    "phases23": "Phases 2-3",
}
subphases = {"start": 90, "middle": 90, "end": 90}
experiences = [
    "familiar_phase12",
    "first_shortcut",
    "shortcut_phase3",
    "familiar_phase3",
]
experiences_labels = {
    "familiar_phase12": "Familiar 1 + 2",
    "first_shortcut": "First Shortcut",
    "shortcut_phase3": "Shortcut Phase 3",
    "familiar_phase3": "Familiar Phase 3",
}
on_task = [
    "familiar_phase12",
    "first_shortcut",
    "phase3_after",
]
on_task_labels = {
    "familiar_phase12": "Phases 1 + 2",
    "first_shortcut": "First Shortcut",
    "phase3_after": "Phase 3 After",
}
event_labels = {
    "led1": "TTL Output on AcqSystem1_0 board 0 port 2 value (0x0001).",
    "led2": "TTL Output on AcqSystem1_0 board 0 port 2 value (0x0002).",
    "ledoff": "TTL Output on AcqSystem1_0 board 0 port 2 value (0x0000).",
    "pb1id": "TTL Input on AcqSystem1_0 board 0 port 1 value (0x0040).",
    "pb2id": "TTL Input on AcqSystem1_0 board 0 port 1 value (0x0020).",
    "pboff": "TTL Input on AcqSystem1_0 board 0 port 1 value (0x0000).",
    "feeder1": "TTL Output on AcqSystem1_0 board 0 port 0 value (0x0004).",
    "feeder2": "TTL Output on AcqSystem1_0 board 0 port 0 value (0x0040).",
    "feederoff": "TTL Output on AcqSystem1_0 board 0 port 0 value (0x0000).",
    "start": "Starting Recording",
    "stop": "Stopping Recording",
}
colors = dict(
    both="k",
    u="#0072b2",
    light_u="#16abff",
    only_u="#0072b2",
    matched_u="#0072b2",
    shortcut="#78c679",
    shortcut1="#78c679",
    full_shortcut="#009e73",
    shortcut2="#009e73",
    only_full_shortcut="#009e73",
    matched_full_shortcut="#009e73",
    joined="#d7301f",
    exploratory="#525252",
    difference="#525252",
    contrast="#525252",
    novel="#d55e00",
    novel1="#d55e00",
    feeders="#dd3497",
    u_feeder1="#fa9fb5",
    u_feeder2="#fcc5c0",
    full_shortcut_feeder1="#fa9fb5",
    full_shortcut_feeder2="#fcc5c0",
    pedestal="#ffeda0",
    other="#ece2f0",
    rest="#bdbdbd",
    run="#737373",
    start="#bdbdbd",
    middle="#969696",
    end="#737373",
)
fontsize = 20
fontsize_small = 15
behavioral_trajectories = ["u", "full_shortcut", "novel"]
barriers = {"shortcut1": "shortcut", "shortcut2": "shortcut", "novel1": "novel"}
barrier_labels = {
    "shortcut1": "Shortcut 1",
    "shortcut2": "Shortcut 2",
    "novel1": "Dead-end",
}
barrier_trajectories = ["shortcut", "novel", "baseline"]
trajectories = ["u", "full_shortcut"]
exclusive_trajectories = ["only_u", "only_full_shortcut", "both"]
matched_trajectories = ["matched_u", "matched_full_shortcut"]
trajectories_labels = {
    "u": "Familiar",
    "only_u": "Familiar",
    "shortcut": "Shortcut",
    "full_shortcut": "Shortcut",
    "only_full_shortcut": "Shortcut",
    "novel": "Dead-end",
    "exploratory": "Other",
}
title_labels = {
    "day1": "Day 1",
    "day2": "Day 2",
    "day3": "Day 3",
    "day4": "Day 4",
    "day5": "Day 5",
    "day6": "Day 6",
    "day7": "Day 7",
    "day4_beh": "Day 4",
    "day5_beh": "Day 5",
    "day6_beh": "Day 6",
    "day7_beh": "Day 7",
    "day8": "Day 8",
    "r063": "R063",
    "r066": "R066",
    "r067": "R067",
    "r067beh": "R067",
    "r068": "R068",
    "full_standard": "Full Standard",
    "short_standard": "Short Standard",
}
trial_types = [
    "u",
    "full_shortcut",
    "novel",
    "exploratory",
]
trial_types_labels = {
    "u": "Familiar",
    "full_shortcut": "Shortcut",
    "novel": "Dead-end",
    "exploratory": "Other",
}
all_zones = [
    "u",
    "shortcut",
    "full_shortcut",
    "novel",
    "u_feeder1",
    "full_shortcut_feeder1",
    "u_feeder2",
    "full_shortcut_feeder2",
    "exploratory",
]
alpha = 0.05
stats_trajectory_groupings = [
    ("u", "full_shortcut"),
    ("u", "novel"),
    ("full_shortcut", "novel"),
]
full_standard_points = {
    "min": -10,
    "feeder1": 0,
    "shortcut1": 20,
    "turn1": 40,
    "turn2": 60,
    "shortcut2": 80,
    "feeder2": 100,
    "max": 110,
}
short_standard_points = {
    "min": 10,
    "feeder1": 20,
    "turn1": 40,
    "turn2": 60,
    "shortcut2": 80,
    "feeder2": 100,
    "max": 110,
}

tex_ids = {
    "all": "all",
    "combined": "combined",
    "full_standard": "fullmaze",
    "short_standard": "shortmaze",
    "r063": "ratone",
    "r066": "rattwo",
    "r067": "ratthree",
    "r067beh": "ratthreebeh",
    "r068": "ratfour",
    "day1": "dayone",
    "day2": "daytwo",
    "day3": "daythree",
    "day4": "dayfour",
    "day4_beh": "dayfourbeh",
    "day5": "dayfive",
    "day5_beh": "dayfivebeh",
    "day6": "daysix",
    "day6_beh": "daysixbeh",
    "day7": "dayseven",
    "day7_beh": "daysevenbeh",
    "day8": "dayeight",
    "prerecord": "prerecord",
    "phase1": "phaseone",
    "pauseA": "pauseA",
    "phase2": "phasetwo",
    "pauseB": "pauseB",
    "phase3": "phasethree",
    "postrecord": "postrecord",
}
rasterize_dpi = 300
# --- Variables

# load_info
n_adjust_points = 9

# load_data
load_questionable = False
max_rate = 5.0
min_spikes = 100

# find_trajectories
merge_gap = 10.0

# cache_tuning_curves
t_smooth = 0.8
min_neurons = 3
min_n_spikes = 50
speed_limit = 8.0
min_hz = 1.5
consecutive_bins = 5
peak_hz_above = 2
tc_binsize = 3
std_gaussian_std = 1
gaussian_std = 3
min_occupancy = 0.4
std_min_occupancy = 0.25

# cache_std_tuning_curves
std_speed_limit = 3.0
std_rest_limit = 5.0
std_tc_binsize = 1
std_t_smooth = 0.5
linear_bin_edges = np.arange(0, 101, std_tc_binsize)
tc_extra_bins_before = 10
tc_extra_bins_after = 7
tc_linear_bin_edges = np.arange(
    -tc_extra_bins_before, 101 + tc_extra_bins_after, std_tc_binsize
)
linear_bin_centers = (
    linear_bin_edges[:-1] + (linear_bin_edges[1:] - linear_bin_edges[:-1]) / 2
)
tc_linear_bin_centers = (
    tc_linear_bin_edges[:-1] + (tc_linear_bin_edges[1:] - tc_linear_bin_edges[:-1]) / 2
)

# analyze_swrs
n_shuffles = 1000
n_likelihood_shuffles = 250
min_n_active = 4
significant = 5.0

# TODO: where used?
binsize = 3

swr_overtime_dt = 30
swr_buffer = 0.15

# define_zones
expand_by = 12
feeder_scale = 1.6
feeder_dist = expand_by * feeder_scale * 0.5
pedestal_scale = 2.2

# decoding
counts_gaussian = 0.005
min_decoding_neurons = 2
min_decoding_spikes = 2
# Previously:
# t_window = 0.05  # 0.1 for running, 0.025 for swr
decoding_dt = 0.01  # 0.02
decoding_window = 0.05  # 0.1

# behavior_bytrial
first_n_trials = 20
first_n_trials_consecutive = 80

# behavior_mostly_shortcut
mostly_thresh = 0.6
mostly_n_trials = 5

# 2D tc plot
n_bins = 100

# trials
trial_min_prop = 0.75
novel_min_duration = 8.0
exploratory_max_duration = 35.0

std_axvlines = {
    "full_shortcut": [0, 20, 80, 100],
    "u": [0, 20, 40, 60, 80, 100],
    "only_full_shortcut": [0, 20, 80, 100],
    "only_u": [0, 20, 40, 60, 80, 100],
}
ticks = [0, 20, 40, 60, 80, 100]

xtickrotation = 45

plot_all = False
full_shuffle = True
