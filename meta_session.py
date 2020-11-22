# pylint: disable=attribute-defined-outside-init, no-member

import json
import os

import nept
import numpy as np

import meta
import paths


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def new_key(key, idx):
    if idx != 0:
        return "{}-{:d}".format(key, idx)
    return key


def fix_problem_pts(info):
    n_points = meta.n_adjust_points
    assert n_points % 2 == 1, "n_points should be odd"

    for key, (direction, radius) in info.problem_path_pts.items():
        point = info.path_pts.pop(key)

        if direction == "down-left":
            theta = (0, np.pi * 0.5)
            center = (point[0] - radius, point[1] - radius)
        elif direction == "left-down":
            theta = (np.pi * 0.5, 0)
            center = (point[0] - radius, point[1] - radius)
        elif direction == "down-right":
            theta = (np.pi, np.pi * 0.5)
            center = (point[0] + radius, point[1] - radius)
        elif direction == "right-down":
            theta = (np.pi * 0.5, np.pi)
            center = (point[0] + radius, point[1] - radius)
        elif direction == "up-left":
            theta = (2 * np.pi, np.pi * 1.5)
            center = (point[0] - radius, point[1] + radius)
        elif direction == "left-up":
            theta = (np.pi * 1.5, 2 * np.pi)
            center = (point[0] - radius, point[1] + radius)
        elif direction == "up-right":
            theta = (np.pi, np.pi * 1.5)
            center = (point[0] + radius, point[1] + radius)
        elif direction == "right-up":
            theta = (np.pi * 1.5, np.pi)
            center = (point[0] + radius, point[1] + radius)
        else:
            raise ValueError("Direction {} not recognized".format(repr(direction)))

        theta = np.linspace(theta[0], theta[1], n_points)
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)
        for i in range(n_points):
            info.path_pts[new_key(key, i - n_points // 2)] = x[i], y[i]

        for traj in info.trajectories.values():
            if key in traj:
                idx = traj.index(key)
                del traj[idx]
                for i in reversed(range(n_points)):
                    traj.insert(idx, new_key(key, i - n_points // 2))


def load_info(filename):
    if not filename.startswith("r0"):
        filename = os.path.basename(filename)

    path = os.path.join(paths.info_dir, filename)
    with open(path) as fp:
        info = AttrDict(json.load(fp))

    info.path = path
    info.path_pts = {
        k: tuple(info.path_pts[v]) if isinstance(v, str) else tuple(v)
        for k, v in info.path_pts.items()
    }

    info.xedges = np.arange(info.xedges[0], info.xedges[1] + meta.binsize, meta.binsize)
    info.yedges = np.arange(info.yedges[0], info.yedges[1] + meta.binsize, meta.binsize)

    info.xcenters = info.xedges[:-1] + (info.xedges[1:] - info.xedges[:-1]) / 2
    info.ycenters = info.yedges[:-1] + (info.yedges[1:] - info.yedges[:-1]) / 2

    info.trajectories = AttrDict(info.trajectories)
    info.trials = AttrDict(info.trials)

    if hasattr(info, "problem_path_pts"):
        fix_problem_pts(info)

    for traj in info.trajectories:
        info.trajectories[traj] = [info.path_pts[s] for s in info.trajectories[traj]]

    if hasattr(info, "problem_positions"):
        info.problem_positions = nept.Epoch(
            [info.problem_positions[0]], [info.problem_positions[1]]
        )

    return info


r063d2 = load_info("r063d2.json")
r063d3 = load_info("r063d3.json")
r063d4 = load_info("r063d4.json")
r063d5 = load_info("r063d5.json")
r063d6 = load_info("r063d6.json")
r063d7 = load_info("r063d7.json")
r063d8 = load_info("r063d8.json")
r066d1 = load_info("r066d1.json")
r066d2 = load_info("r066d2.json")
r066d3 = load_info("r066d3.json")
r066d4 = load_info("r066d4.json")
r066d5 = load_info("r066d5.json")
r066d6 = load_info("r066d6.json")
r066d7 = load_info("r066d7.json")
r066d8 = load_info("r066d8.json")
r067d1 = load_info("r067d1.json")
r067d2 = load_info("r067d2.json")
r067d3 = load_info("r067d3.json")
r067d4 = load_info("r067d4.json")
r067d5 = load_info("r067d5.json")
r067d6 = load_info("r067d6.json")
r067d7 = load_info("r067d7.json")
r067d8 = load_info("r067d8.json")
r068d1 = load_info("r068d1.json")
r068d2 = load_info("r068d2.json")
r068d3 = load_info("r068d3.json")
r068d4 = load_info("r068d4.json")
r068d5 = load_info("r068d5.json")
r068d6 = load_info("r068d6.json")
r068d7 = load_info("r068d7.json")
r068d8 = load_info("r068d8.json")

# only using sessions with >50 neurons total
analysis_infos = [
    r063d2,
    r063d3,
    r063d4,
    r063d5,
    r063d6,
    r063d7,
    r063d8,
    r066d1,
    r066d2,
    r066d3,
    r066d4,
    r066d5,
    r066d6,
    r066d7,
    r066d8,
    r067d1,
    r067d2,
    r067d3,
    r067d8,
    r068d1,
    r068d2,
    r068d3,
    r068d4,
    r068d5,
    r068d6,
    r068d7,
    r068d8,
]

all_infos = [
    r063d2,
    r063d3,
    r063d4,
    r063d5,
    r063d6,
    r063d7,
    r063d8,
    r066d1,
    r066d2,
    r066d3,
    r066d4,
    r066d5,
    r066d6,
    r066d7,
    r066d8,
    r067d1,
    r067d2,
    r067d3,
    r067d4,
    r067d5,
    r067d6,
    r067d7,
    r067d8,
    r068d1,
    r068d2,
    r068d3,
    r068d4,
    r068d5,
    r068d6,
    r068d7,
    r068d8,
]

r063_infos = [
    r063d2,
    r063d3,
    r063d4,
    r063d5,
    r063d6,
    r063d7,
    r063d8,
]

r066_infos = [
    r066d1,
    r066d2,
    r066d3,
    r066d4,
    r066d5,
    r066d6,
    r066d7,
    r066d8,
]

r067_infos = [
    r067d1,
    r067d2,
    r067d3,
    r067d8,
]

r067_infos_beh = [
    r067d1,
    r067d2,
    r067d3,
    r067d4,
    r067d5,
    r067d6,
    r067d7,
    r067d8,
]

r068_infos = [
    r068d1,
    r068d2,
    r068d3,
    r068d4,
    r068d5,
    r068d6,
    r068d7,
    r068d8,
]

day1_infos = [
    r066d1,
    r067d1,
    r068d1,
]

day2_infos = [
    r063d2,
    r066d2,
    r067d2,
    r068d2,
]

day3_infos = [
    r063d3,
    r066d3,
    r067d3,
    r068d3,
]

day4_infos = [
    r063d4,
    r066d4,
    r068d4,
]

day4_infos_beh = [
    r063d4,
    r066d4,
    r067d4,
    r068d4,
]

day5_infos = [
    r063d5,
    r066d5,
    r068d5,
]

day5_infos_beh = [
    r063d5,
    r066d5,
    r067d5,
    r068d5,
]

day6_infos = [
    r063d6,
    r066d6,
    r068d6,
]

day6_infos_beh = [
    r063d6,
    r066d6,
    r067d6,
    r068d6,
]

day7_infos = [
    r063d7,
    r066d7,
    r068d7,
]

day7_infos_beh = [
    r063d7,
    r066d7,
    r067d7,
    r068d7,
]

day8_infos = [
    r063d8,
    r066d8,
    r067d8,
    r068d8,
]

full_standard_infos = day1_infos + day5_infos + day6_infos + day7_infos + day8_infos

short_standard_infos = day2_infos + day3_infos + day4_infos

all_grouped = {"all": all_infos}
analysis_grouped = {"combined": analysis_infos}
days_grouped = {
    "day1": day1_infos,
    "day2": day2_infos,
    "day3": day3_infos,
    "day4": day4_infos,
    "day5": day5_infos,
    "day6": day6_infos,
    "day7": day7_infos,
    "day4_beh": day4_infos_beh,
    "day5_beh": day5_infos_beh,
    "day6_beh": day6_infos_beh,
    "day7_beh": day7_infos_beh,
    "day8": day8_infos,
}
rats_grouped = {
    "r063": r063_infos,
    "r066": r066_infos,
    "r067": r067_infos,
    "r067beh": r067_infos_beh,
    "r068": r068_infos,
}
groups = {
    "full_standard": full_standard_infos,
    "short_standard": short_standard_infos,
}
groups.update(all_grouped)
groups.update(analysis_grouped)
groups.update(days_grouped)
groups.update(rats_grouped)
