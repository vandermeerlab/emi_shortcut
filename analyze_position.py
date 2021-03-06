import nept
import numpy as np
import scipy.stats
import statsmodels.api as sm
from shapely.geometry import Point

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


def dist_2d(pt1, pt2):
    return np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)


@task(infos=meta_session.all_infos, cache_saves="barrier_t")
def cache_barrier_t(info, *, task_times, position):
    dt = np.median(np.diff(position.time))
    position = position[task_times["phase2"]]
    t = {}

    for barrier in meta.barriers:
        barrier_xy = info.path_pts[barrier]
        dist = dist_2d(barrier_xy, position.data.T)
        n_points = np.sum(dist < meta.expand_by).item()
        t[barrier] = n_points * dt

    return t


@task(groups=meta_session.groups, cache_saves="barrier_t")
def cache_combined_barrier_t(infos, group_name, *, all_barrier_t):
    return aggregate.combine_with_append(all_barrier_t)


@task(infos=meta_session.all_infos, cache_saves="barrier_time_bytrial")
def cache_barrier_time_bytrial(info, *, trials, task_times, position):
    dt = np.median(np.diff(position.time))
    position = position[task_times["phase2"]]
    trials = trials["u"].time_slice(
        task_times["phase2"].start, task_times["phase2"].stop
    )
    t = {}

    for barrier in meta.barriers:
        barrier_xy = info.path_pts[barrier]
        t[barrier] = []
        for trial in trials:
            trial_pos = position[trial]
            dist = dist_2d(barrier_xy, trial_pos.data.T)
            n_points = np.sum(dist < meta.expand_by).item()
            t[barrier].append(n_points * dt)

    return t


@task(groups=meta_session.groups, cache_saves="barrier_time_bytrial")
def cache_combined_barrier_time_bytrial(infos, group_name, *, all_barrier_time_bytrial):
    all_t = {}
    for barrier in meta.barriers:
        max_trials = max(len(time[barrier]) for time in all_barrier_time_bytrial)
        all_t[barrier] = []
        for i in range(max_trials):
            all_t[barrier].append(
                [
                    time[barrier][i]
                    for time in all_barrier_time_bytrial
                    if len(time[barrier]) > i
                ]
            )

    return all_t


@task(infos=meta_session.all_infos, cache_saves="shortcut_time_bytrial")
def cache_shortcut_time_bytrial(info, *, trials, task_times, position, zones):
    dt = np.median(np.diff(position.time))
    position = position[task_times["phase3"]]
    t = []

    for trial in trials["full_shortcut"]:
        trial_pos = position[trial]
        trial_t = 0
        for pos_idx in range(trial_pos.n_samples):
            if zones["shortcut"].contains(Point(trial_pos.data[pos_idx])):
                trial_t += dt
        t.append(trial_t)

    return t


@task(groups=meta_session.groups, cache_saves="shortcut_time_bytrial")
def cache_combined_shortcut_time_bytrial(
    infos, group_name, *, all_shortcut_time_bytrial
):
    max_trials = max(len(time) for time in all_shortcut_time_bytrial)
    all_t = []
    for i in range(max_trials):
        all_t.append([time[i] for time in all_shortcut_time_bytrial if len(time) > i])
    return all_t


@task(infos=meta_session.all_infos, cache_saves="barrier_dist_to_feeder")
def cache_barrier_dist_to_feeder(info, *, task_times):
    dist = {}
    feeder1_xy = info.path_pts["feeder1"]
    feeder2_xy = info.path_pts["feeder2"]

    for barrier in meta.barriers:
        barrier_xy = info.path_pts[barrier]
        dist[barrier] = min(
            dist_2d(barrier_xy, feeder1_xy), dist_2d(barrier_xy, feeder2_xy)
        )

    return dist


@task(groups=meta_session.groups, cache_saves="barrier_dist_to_feeder")
def cache_combined_barrier_dist_to_feeder(
    infos, group_name, *, all_barrier_dist_to_feeder
):
    return aggregate.combine_with_append(all_barrier_dist_to_feeder)


@task(infos=meta_session.all_infos, cache_saves="barrier_time")
def cache_barrier_time(info, *, task_times, position):
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
        dist = dist_2d(barrier_xy, position.data.T)
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


@task(infos=meta_session.all_infos, cache_saves="speed_overtime")
def cache_speed_overtime(info, *, position, task_times):
    return position.speed(t_smooth=meta.speed_overtime_dt)[task_times["maze_times"]]


@task(infos=meta_session.all_infos, cache_saves="stop_rate")
def cache_stop_rate(info, *, position, task_times):
    stop_rate = {}
    for run_time in meta.run_times:
        pos = position[task_times[run_time]]
        rest = nept.rest_threshold(pos, thresh=meta.speed_limit, t_smooth=meta.t_smooth)
        stop_rate[run_time] = (
            rest.n_epochs / np.sum(task_times[run_time].durations)
        ) * 60
    return stop_rate


@task(groups=meta_session.groups, cache_saves="stop_rate")
def cache_combined_stop_rate(infos, group_name, *, all_stop_rate):
    return aggregate.combine_with_append(all_stop_rate)
