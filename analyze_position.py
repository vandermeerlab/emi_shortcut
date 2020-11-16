import re

import nept
import numpy as np
from shapely.geometry import Point
import scipy.stats
import statsmodels.api as sm

import aggregate
import meta
import meta_session
from tasks import task
from utils import latex_float


@task(infos=meta_session.all_infos, cache_saves="raw_position_byzone")
def cache_raw_position_byzone(info, *, position, raw_trials, zones):
    """Cache position_byzone in .pkl"""
    position = position[raw_trials]

    idx = {zone: [] for zone in meta.all_zones}
    for pos_idx in range(position.n_samples):
        point = Point(position.data[pos_idx])
        in_feeder = False
        if zones["u_feeder1"].contains(point):
            idx["u_feeder1"].append(pos_idx)
            in_feeder = True
        elif zones["u_feeder2"].contains(point):
            idx["u_feeder2"].append(pos_idx)
            in_feeder = True

        if zones["full_shortcut_feeder1"].contains(point):
            idx["full_shortcut_feeder1"].append(pos_idx)
            in_feeder = True
        elif zones["full_shortcut_feeder2"].contains(point):
            idx["full_shortcut_feeder2"].append(pos_idx)
            in_feeder = True

        if in_feeder:
            continue
        elif zones["novel"].contains(point):
            idx["novel"].append(pos_idx)
        elif zones["full_shortcut"].contains(point):
            idx["full_shortcut"].append(pos_idx)
        elif zones["u"].contains(point):
            idx["u"].append(pos_idx)
        else:
            idx["exploratory"].append(pos_idx)

    position_byzone = {zone: position[idx[zone]] for zone in meta.all_zones}
    position_byzone["u_feeders"] = position_byzone["u_feeder1"].combine(
        position_byzone["u_feeder2"]
    )
    position_byzone["full_shortcut_feeders"] = position_byzone[
        "full_shortcut_feeder1"
    ].combine(position_byzone["full_shortcut_feeder2"])
    return position_byzone


@task(infos=meta_session.all_infos, cache_saves="position_byzone")
def cache_position_byzone(info, *, position, raw_position_byzone, trials, zones):
    """Cache position_byzone in .pkl"""
    # 'novel' and 'full_shortcut' trials in raw_position_byzone are good
    # but 'u' has overlapping regions cut out, so we re-zone 'u' trials
    # to capture all points in the 'u' trajectory (but not the feeders)
    position_byzone = raw_position_byzone

    other_trials = nept.Epoch([], [])
    for trial_type in trials:
        if trial_type != "u":
            other_trials = other_trials.join(trials[trial_type])

    # Remove 'u' trials from position_byzone
    for zone in meta.all_zones:
        position_byzone[zone] = position_byzone[zone][other_trials]

    # Re-classify 'u' trials using the same logic as before, but changing the order
    # of the if statements such that 'u' takes precedence
    position = position[trials["u"]]
    idx = {zone: [] for zone in meta.all_zones}
    for pos_idx in range(position.n_samples):
        point = Point(position.data[pos_idx])
        in_feeder = False
        if zones["u_feeder1"].contains(point):
            idx["u_feeder1"].append(pos_idx)
            in_feeder = True
        elif zones["u_feeder2"].contains(point):
            idx["u_feeder2"].append(pos_idx)
            in_feeder = True

        if zones["full_shortcut_feeder1"].contains(point):
            idx["full_shortcut_feeder1"].append(pos_idx)
            in_feeder = True
        elif zones["full_shortcut_feeder2"].contains(point):
            idx["full_shortcut_feeder2"].append(pos_idx)
            in_feeder = True

        if in_feeder:
            continue
        elif zones["u"].contains(point):
            idx["u"].append(pos_idx)
        elif zones["novel"].contains(point):
            idx["novel"].append(pos_idx)
        elif zones["full_shortcut"].contains(point):
            idx["full_shortcut"].append(pos_idx)
        else:
            idx["exploratory"].append(pos_idx)
    for zone in meta.all_zones:
        position_byzone[zone] = position_byzone[zone].combine(position[idx[zone]])

    return position_byzone


@task(infos=meta_session.all_infos, cache_saves="speed_byphase")
def cache_speed_byphase(info, *, task_times, position):
    speed_byphase = {}
    for phase in meta.task_times:
        this_position = position[task_times[phase]]
        speed_byphase[phase] = np.mean(this_position.speed().data)
    return speed_byphase


@task(infos=meta_session.all_infos, cache_saves="speed_byphase_restonly")
def cache_speed_byphase_restonly(info, *, task_times, position):
    speed_byphase = {}
    rest = nept.rest_threshold(
        position, thresh=meta.std_rest_limit, t_smooth=meta.t_smooth
    )
    for phase in meta.task_times:
        this_position = position[task_times[phase].intersect(rest)]
        speed_byphase[phase] = np.mean(this_position.speed().data)
    return speed_byphase


@task(groups=meta_session.groups, cache_saves="speed_byphase")
def cache_combined_speed_byphase(infos, group_name, *, all_speed_byphase):
    return aggregate.combine_with_append(all_speed_byphase)


@task(groups=meta_session.groups, cache_saves="speed_byphase_restonly")
def cache_combined_speed_byphase_restonly(
    infos, group_name, *, all_speed_byphase_restonly
):
    return aggregate.combine_with_append(all_speed_byphase_restonly)


@task(infos=meta_session.all_infos, cache_saves="barrier_time")
def cache_barrier_time(info, *, task_times, position, zones):
    dt = np.median(np.diff(position.time))
    position = position[task_times["phase2"]]
    barriers = dict(meta.barriers)
    barriers.update(
        {
            path_pt: "baseline"
            for path_pt in info.path_pts
            if path_pt
            not in list(meta.barriers) + ["error", "pedestal", "feeder1", "feeder2"]
        }
    )

    barrier_time = {trajectory: 0 for trajectory in meta.barrier_trajectories}
    for barrier, trajectory in barriers.items():
        barrier_xy = info.path_pts[barrier]
        dist = np.sqrt(
            (barrier_xy[0] - position.x) ** 2 + (barrier_xy[1] - position.y) ** 2
        )
        n_points = np.sum(dist < meta.expand_by).item()
        barrier_time[trajectory] += n_points * dt

    # Normalize by the number of barriers
    for trajectory in barrier_time:
        barrier_time[trajectory] /= sum(v == trajectory for v in barriers.values())

    return barrier_time


@task(groups=meta_session.groups, cache_saves="barrier_time")
def cache_combined_barrier_time(infos, group_name, *, all_barrier_time):
    return aggregate.combine_with_append(all_barrier_time)


@task(groups=meta_session.all_grouped, savepath=("behavior", "barrier_time.tex"))
def save_barrier_time(infos, group_name, *, barrier_time, all_barrier_time, savepath):
    with open(savepath, "w") as fp:
        print("% Average time spent by a barrier", file=fp)
        for info, this_barrier_time in zip(infos, all_barrier_time):
            print(f"% {info.session_id}", file=fp)
            for trajectory in barrier_time:
                print(f"% {trajectory}: {this_barrier_time[trajectory]}", file=fp)
            print("% ---------", file=fp)
        print("% Combined", file=fp)
        for trajectory in barrier_time:
            traj = trajectory.replace("_", "")
            print(
                fr"\def \mean{traj}barrier/{{{np.mean(barrier_time[trajectory]):.1f}}}",
                file=fp,
            )
            print(
                fr"\def \sem{traj}barrier/{{{scipy.stats.sem(barrier_time[trajectory]):.1f}}}",
                file=fp,
            )
        t, pval, df = sm.stats.ttest_ind(
            barrier_time["shortcut"], barrier_time["novel"]
        )
        pval = latex_float(pval)
        print(
            fr"\def \allbarrierststat/{{{t:.2f}}}",
            file=fp,
        )
        print(
            fr"\def \allbarrierspval/{{{pval}}}",
            file=fp,
        )
        print(
            fr"\def \allbarriersdf/{{{int(df)}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(
    groups={"day7_beh": meta_session.day7_infos_beh},
    savepath=("behavior", "barrier_time_day7.tex"),
)
def save_barrier_time_day7(
    infos, group_name, *, barrier_time, all_barrier_time, savepath
):
    with open(savepath, "w") as fp:
        print("% Average time spent by a barrier", file=fp)
        for info, this_barrier_time in zip(infos, all_barrier_time):
            print(f"% {info.session_id}", file=fp)
            for trajectory in barrier_time:
                print(f"% {trajectory}: {this_barrier_time[trajectory]}", file=fp)
            print("% ---------", file=fp)
        print("% Combined", file=fp)
        for trajectory in barrier_time:
            traj = trajectory.replace("_", "")
            print(
                fr"\def \mean{traj}barrierdayseven/{{{np.mean(barrier_time[trajectory]):.1f}}}",
                file=fp,
            )
            print(
                fr"\def \sem{traj}barrierdayseven/{{{scipy.stats.sem(barrier_time[trajectory]):.1f}}}",
                file=fp,
            )
        t, pval, df = sm.stats.ttest_ind(
            barrier_time["shortcut"], barrier_time["novel"]
        )
        pval = latex_float(pval)
        print(
            fr"\def \barrierdaysevenstat/{{{t:.2f}}}",
            file=fp,
        )
        print(
            fr"\def \barrierdaysevenpval/{{{pval}}}",
            file=fp,
        )
        print(
            fr"\def \barrierdaysevendf/{{{int(df)}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(infos=meta_session.all_infos)
def print_missing_positions(info, *, task_times, position):
    for task_time in meta.task_times:
        dts = np.sort(np.diff(position[task_times[task_time]].time))
        if dts[-1] > 5:
            all_above = dts[dts > 5]
            print(
                f"Found {all_above.size} gaps of 5+ seconds for {info.session_id} "
                f"during {task_time}:"
            )
            print(f"  {all_above.tolist()}")
