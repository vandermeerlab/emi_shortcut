import nept
import numpy as np
import pandas as pd
import scipy.io
import statsmodels.formula.api as smf
from shapely.geometry import Point

import aggregate
import meta
import meta_session
import paths
from tasks import task
from utils import ranksum_test


@task(infos=meta_session.all_infos, cache_saves="swrs")
def cache_swrs(info, *, task_times):
    swrs = scipy.io.loadmat(paths.swr_file(info))
    starts = swrs["evt"][0][0][1]
    stops = swrs["evt"][0][0][2]
    return nept.Epoch(starts, stops).merge().intersect(task_times["all"])


@task(infos=meta_session.all_infos, cache_saves="swrs_byzone")
def cache_swrs_byzone(info, *, task_times, swrs, position, trials, zones):
    swrs_byzone = {zone: nept.Epoch([], []) for zone in meta.all_zones}

    for i, center in enumerate(swrs.centers):
        if not task_times["maze_times"].contains(center):
            continue

        def classify(zone, i):
            swrs_byzone[zone] = swrs_byzone[zone].join(swrs[i])

        point = Point(*position[nept.find_nearest_idx(position.time, center)].data)
        if zones["u_feeder1"].contains(point) or zones[
            "full_shortcut_feeder1"
        ].contains(point):
            classify("u_feeder1", i)
            classify("full_shortcut_feeder1", i)
        elif zones["u_feeder2"].contains(point) or zones[
            "full_shortcut_feeder2"
        ].contains(point):
            classify("u_feeder2", i)
            classify("full_shortcut_feeder2", i)
        elif trials["u"].contains(center) and zones["u"].contains(point):
            classify("u", i)
        elif zones["novel"].contains(point):
            classify("novel", i)
        elif zones["full_shortcut"].contains(point):
            classify("full_shortcut", i)
        elif zones["u"].contains(point):
            classify("u", i)
        else:
            classify("exploratory", i)

    swrs_byzone["u_feeders"] = swrs_byzone["u_feeder1"].join(swrs_byzone["u_feeder2"])
    swrs_byzone["full_shortcut_feeders"] = swrs_byzone["full_shortcut_feeder1"].join(
        swrs_byzone["full_shortcut_feeder2"]
    )

    return swrs_byzone


def get_swr_rate_byzone(info, swrs_byzone, position, trials, restonly):
    rate_byzone = {}
    n_swrs_byzone = {}
    rest = nept.rest_threshold(
        position, thresh=meta.std_rest_limit, t_smooth=meta.t_smooth
    )
    for trajectory in meta.trajectories:
        this_trials = trials[trajectory]
        swrs = swrs_byzone[trajectory]
        if restonly:
            swrs = swrs.intersect(rest)
            this_trials.intersect(rest)

        n_swrs_byzone[trajectory] = swrs.n_epochs
        rate_byzone[trajectory] = swrs.n_epochs / np.sum(this_trials.durations)

    return rate_byzone, n_swrs_byzone


@task(infos=meta_session.all_infos, cache_saves=["swr_rate_byzone", "swr_n_byzone"])
def cache_swr_rate_byzone(info, *, swrs_byzone, position, trials):
    rates, n = get_swr_rate_byzone(info, swrs_byzone, position, trials, restonly=False)
    return {"swr_rate_byzone": rates, "swr_n_byzone": n}


@task(groups=meta_session.analysis_grouped, cache_saves="swr_rate_byzone")
def cache_combined_swr_rate_byzone(infos, group_name, *, all_swr_rate_byzone):
    return aggregate.combine_with_append(all_swr_rate_byzone)


@task(groups=meta_session.analysis_grouped, cache_saves="swr_n_byzone")
def cache_combined_swr_n_byzone(infos, group_name, *, all_swr_n_byzone):
    return aggregate.combine_with_sum(all_swr_n_byzone)


@task(
    infos=meta_session.all_infos,
    cache_saves=["swr_rate_byzone_restonly", "swr_n_byzone_restonly"],
)
def cache_swr_rate_byzone_restonly(info, *, swrs_byzone, position, trials):
    rates, n = get_swr_rate_byzone(info, swrs_byzone, position, trials, restonly=True)
    return {"swr_rate_byzone_restonly": rates, "swr_n_byzone_restonly": n}


@task(groups=meta_session.analysis_grouped, cache_saves="swr_rate_byzone_restonly")
def cache_combined_swr_rate_byzone_restonly(
    infos, group_name, *, all_swr_rate_byzone_restonly
):
    return aggregate.combine_with_append(all_swr_rate_byzone_restonly)


@task(groups=meta_session.analysis_grouped, cache_saves="swr_n_byzone_restonly")
def cache_combined_swr_n_byzone_restonly(
    infos, group_name, *, all_swr_n_byzone_restonly
):
    return aggregate.combine_with_sum(all_swr_n_byzone_restonly)


def get_swr_correlation(swr_spikes):
    rng = np.random.RandomState(meta.seed)
    active = [len(spikes.time) > 0 for spikes in swr_spikes]
    if np.sum(active) < meta.min_n_active:
        return (
            np.nan,
            np.nan,
            np.ones(meta.n_shuffles + 1) * np.nan,
            np.ones(meta.n_shuffles + 1) * np.nan,
        )

    spikes_tc_idx = []
    for i in range(len(swr_spikes)):
        for time in swr_spikes[i].time:
            spikes_tc_idx.append((time, i))
    spikes_tc_idx.sort(key=lambda tup: tup[0])
    this_swr = [tc_idx for _, tc_idx in spikes_tc_idx]
    template_swr = list(sorted(this_swr))

    assert len(template_swr) >= meta.min_n_active

    val, p = scipy.stats.spearmanr(this_swr, template_swr)

    shuffled_val, shuffled_p = [], []
    for _ in range(meta.n_shuffles + 1):
        shuffled = rng.choice(template_swr, size=len(template_swr), replace=False)
        s_val, s_p = scipy.stats.spearmanr(shuffled, template_swr)
        shuffled_val.append(s_val)
        shuffled_p.append(s_p)

    return val, p, shuffled_val, shuffled_p


@task(
    infos=meta_session.all_infos,
    cache_saves=[
        "swr_correlations",
        "swr_correlations_p",
        "swr_correlations_shuffled",
        "swr_correlations_shuffled_p",
    ],
)
def cache_swr_correlations(info, *, swrs, matched_tc_spikes):
    swr_correlations = {}
    swr_correlations_p = {}
    swr_correlations_shuffled = {}
    swr_correlations_shuffled_p = {}

    for trajectory in meta.trajectories:
        correlations = []
        correlations_p = []
        shuffled = []
        shuffled_p = []

        for swr in swrs:
            correlation, correlation_p, shuffle, shuffle_p = get_swr_correlation(
                swr_spikes=[
                    spiketrain.time_slice(swr.start, swr.stop)
                    for spiketrain in matched_tc_spikes[trajectory]
                ]
            )
            correlations.append(correlation)
            correlations_p.append(correlation_p)
            shuffled.append(shuffle)
            shuffled_p.append(shuffle_p)

        swr_correlations[trajectory] = np.array(correlations)
        swr_correlations_p[trajectory] = np.array(correlations_p)
        swr_correlations_shuffled[trajectory] = np.array(shuffled)
        swr_correlations_shuffled_p[trajectory] = np.array(shuffled_p)

    return {
        "swr_correlations": swr_correlations,
        "swr_correlations_p": swr_correlations_p,
        "swr_correlations_shuffled": swr_correlations_shuffled,
        "swr_correlations_shuffled_p": swr_correlations_shuffled_p,
    }


@task(groups=meta_session.groups, cache_saves="swr_correlations")
def cache_combined_swr_correlations(infos, group_name, *, all_swr_correlations):
    return {
        trajectory: np.hstack(
            [correlations[trajectory] for correlations in all_swr_correlations]
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="swr_correlation_percentiles")
def cache_combined_swr_correlation_percentiles(
    infos, group_name, *, all_swr_correlation_percentiles
):
    return {
        trajectory: np.hstack(
            [percentiles[trajectory] for percentiles in all_swr_correlation_percentiles]
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="swr_shuffled_percentiles")
def cache_combined_swr_shuffled_percentiles(
    infos, group_name, *, all_swr_shuffled_percentiles
):
    return {
        trajectory: np.hstack(
            [percentiles[trajectory] for percentiles in all_swr_shuffled_percentiles]
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="swr_correlations_shuffled")
def cache_combined_swr_correlations_shuffled(
    infos, group_name, *, all_swr_correlations_shuffled
):
    return {
        trajectory: np.vstack(
            [correlations[trajectory] for correlations in all_swr_correlations_shuffled]
        )
        for trajectory in meta.trajectories
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=[
        "replays",
        "replays_idx",
        "swr_correlation_percentiles",
        "swr_shuffled_percentiles",
    ],
)
def cache_replays(info, *, swrs, swr_correlations, swr_correlations_shuffled):
    replays = {}
    replays_idx = {}
    percentiles = {}
    s_percentiles = {}

    for trajectory in meta.trajectories:
        traj_replays = nept.Epoch([], [])
        traj_replays_idx = []
        traj_percentiles = []
        traj_s_percentiles = []

        for i, (swr, correlation, shuffled) in enumerate(
            zip(
                swrs,
                swr_correlations[trajectory],
                swr_correlations_shuffled[trajectory],
            )
        ):
            if np.isnan(correlation):
                traj_percentiles.append(np.nan)
                traj_s_percentiles.append(np.nan)
                continue

            percentile = scipy.stats.percentileofscore(shuffled, correlation)
            traj_percentiles.append(percentile)
            if percentile <= meta.significant or percentile >= 100 - meta.significant:
                traj_replays = traj_replays.join(swr)
                traj_replays_idx.append(i)
            traj_s_percentiles.append(
                scipy.stats.percentileofscore(shuffled[1:], shuffled[0])
            )
        replays[trajectory] = traj_replays
        replays_idx[trajectory] = traj_replays_idx
        percentiles[trajectory] = np.array(traj_percentiles)
        s_percentiles[trajectory] = np.array(traj_s_percentiles)

    for trajectory in meta.exclusive_trajectories:
        replays[trajectory] = nept.Epoch([], [])
        replays_idx[trajectory] = []

    for i in range(swrs.n_epochs):
        if i in replays_idx["u"] and i in replays_idx["full_shortcut"]:
            replays["both"] = replays["both"].join(swrs[i])
            replays_idx["both"].append(i)
        elif i in replays_idx["u"]:
            replays["only_u"] = replays["only_u"].join(swrs[i])
            replays_idx["only_u"].append(i)
        elif i in replays_idx["full_shortcut"]:
            replays["only_full_shortcut"] = replays["only_full_shortcut"].join(swrs[i])
            replays_idx["only_full_shortcut"].append(i)

    return {
        "replays": replays,
        "replays_idx": replays_idx,
        "swr_correlation_percentiles": percentiles,
        "swr_shuffled_percentiles": s_percentiles,
    }


@task(infos=meta_session.all_infos, cache_saves="joined_replays")
def cache_joined_replays(info, *, replays):
    return replays["u"].join(replays["full_shortcut"]).merge()


@task(infos=meta_session.all_infos, cache_saves="swrs_byphase")
def cache_swrs_byphase(info, *, task_times, swrs):
    return {
        phase: swrs.time_slice(task_times[phase].start, task_times[phase].stop)
        for phase in meta.task_times
    }


@task(infos=meta_session.all_infos, cache_saves="replays_byphase")
def cache_replays_byphase(info, *, task_times, replays):
    return {
        trajectory: {
            phase: replays[trajectory].time_slice(
                task_times[phase].start, task_times[phase].stop
            )
            for phase in meta.task_times
        }
        for trajectory in meta.trajectories + meta.exclusive_trajectories
    }


@task(groups=meta_session.analysis_grouped, cache_saves="replays_byphase_df")
def cache_replays_byphase_df(infos, group_name, *, all_replays_byphase):
    replays_df = []
    for info, replays_byphase in zip(infos, all_replays_byphase):
        for trajectory in meta.trajectories:
            replays_df.extend(
                {
                    "n_replays": replays_byphase[trajectory][phase].n_epochs,
                    "trajectory": trajectory,
                    "phase": phase,
                    "rat_id": info.session_id[:4],
                    "session": info.session_id[-1],
                }
                for phase in meta.task_times
            )
    return pd.DataFrame.from_dict(replays_df)


@task(groups=meta_session.analysis_grouped, savepath=("swrs", "n_swrs_byphase.table"))
def save_n_swrs_byphase(infos, group_name, *, all_swrs_byphase, savepath):
    with open(savepath, "w") as fp:
        print(
            r"""
            \begin{tabular}{c | c c c c c c c}
 \toprule
 \textbf{Rat~ID} & \textbf{Pre-task} & \textbf{Phase1} & \textbf{PauseA} & \textbf{Phase2}
 & \textbf{PauseB} & \textbf{Phase3} & \textbf{Post-task} \\ [0.5ex]
 \midrule
 """.strip(),
            file=fp,
        )
        phase_totals = [0 for _ in range(len(meta.task_times))]
        for info, swrs_byphase in zip(infos, all_swrs_byphase):
            phases = []
            space = " [1ex]" if info.session_id == "R068d8" else ""
            for i, phase in enumerate(meta.task_times):
                phases.append(str(swrs_byphase[phase].n_epochs))
                phase_totals[i] += swrs_byphase[phase].n_epochs
            print(
                rf"\textbf{{{info.session_id}}} & {' & '.join(phases)} \\{space}",
                file=fp,
            )
            if info.session_id in ["R063d8", "R066d8", "R067d8"]:
                print(r"\midrule", file=fp)

        phase_totals = [str(i) for i in phase_totals]
        print(r"\bottomrule", file=fp)
        print(
            rf"\textbf{{Total}} & {' & '.join(phase_totals)} \\",
            file=fp,
        )
        print(r"\bottomrule", file=fp)
        print(r"\end{tabular}", file=fp)


@task(groups=meta_session.analysis_grouped, savepath=("swrs", "swrs_n.tex"))
def save_n_swrs(infos, group_name, *, all_swrs, savepath):
    with open(savepath, "w") as fp:
        print("% Number of SWR events overall", file=fp)

        total_swrs_n = []
        total_swrs_durations = []
        for info, swrs in zip(infos, all_swrs):
            print(f"% {info.session_id}", file=fp)
            print(f"% N swrs: {swrs.n_epochs}", file=fp)
            print(f"% Avg swrs duration: {np.mean(swrs.durations)}", file=fp)
            print("% ---------", file=fp)
            total_swrs_n.append(swrs.n_epochs)
            total_swrs_durations.extend(swrs.durations)

        print("% Combined", file=fp)
        # print(f"Total swrs: {np.sum(total_swrs_n)}", file=fp)
        print(fr"\def \totalnswrs/{{{np.sum(total_swrs_n)}}}", file=fp)
        print(fr"\def \minnswrs/{{{np.min(total_swrs_n)}}}", file=fp)
        print(fr"\def \maxnswrs/{{{np.max(total_swrs_n)}}}", file=fp)
        print(
            fr"\def \meannswrs/{{{np.mean(total_swrs_n):.1f}}}",
            file=fp,
        )
        print(
            fr"\def \meanswrsdurations/{{{np.mean(total_swrs_durations)*1000:.1f}}}",
            file=fp,
        )


@task(groups=meta_session.analysis_grouped, cache_saves="swrs_durations")
def cache_combined_swr_durations(infos, group_name, *, all_swrs):
    durations = []
    for swrs in all_swrs:
        durations.extend(swrs.durations)
    return durations


@task(groups=meta_session.analysis_grouped, cache_saves="replay_durations")
def cache_combined_replay_durations(infos, group_name, *, all_replays):
    durations = {trajectory: [] for trajectory in meta.trajectories}
    for trajectory in meta.trajectories:
        for replay in all_replays:
            durations[trajectory].extend(replay[trajectory].durations)
    return durations


@task(groups=meta_session.analysis_grouped, cache_saves="swr_durations_byphase")
def cache_combined_swr_durations_byphase(infos, group_name, *, all_swrs_byphase):
    durations = {}
    for phase in meta.task_times:
        durations[phase] = []
        for swrs_byphase in all_swrs_byphase:
            durations[phase].extend(swrs_byphase[phase].durations)
    return durations


def get_swr_rate_byphase(task_times, swrs_byphase, position, restonly):
    rate_byphase = {}
    n_swrs_byphase = {}
    rest = nept.rest_threshold(
        position, thresh=meta.std_rest_limit, t_smooth=meta.t_smooth
    )
    for phase in meta.task_times:
        phase_epochs = task_times[phase]
        swrs = swrs_byphase[phase]
        if restonly:
            phase_epochs = phase_epochs.intersect(rest)
            swrs = swrs.intersect(rest)

        n_swrs_byphase[phase] = swrs.n_epochs
        rate_byphase[phase] = swrs.n_epochs / np.sum(phase_epochs.durations)

    return rate_byphase, n_swrs_byphase


@task(infos=meta_session.all_infos, cache_saves=["swr_rate_byphase", "swr_n_byphase"])
def cache_swr_rate_byphase(info, *, task_times, swrs_byphase, position):
    rates, n = get_swr_rate_byphase(task_times, swrs_byphase, position, restonly=False)
    return {"swr_rate_byphase": rates, "swr_n_byphase": n}


def get_combined_swr_rate_byphase(
    all_task_times, all_swrs_byphase, all_position, restonly
):
    rate_byphase = {phase: 0 for phase in meta.task_times}
    total_durations = {phase: 0 for phase in meta.task_times}
    for task_times, swrs_byphase, position in zip(
        all_task_times, all_swrs_byphase, all_position
    ):
        rest = nept.rest_threshold(
            position, thresh=meta.std_rest_limit, t_smooth=meta.t_smooth
        )
        for phase in meta.task_times:
            phase_epochs = task_times[phase]
            swrs = swrs_byphase[phase]
            if restonly:
                phase_epochs = phase_epochs.intersect(rest)
                swrs = swrs.intersect(rest)

            rate_byphase[phase] += swrs.n_epochs
            total_durations[phase] += np.sum(phase_epochs.durations)

    return {
        phase: rate_byphase[phase] / total_durations[phase] for phase in meta.task_times
    }


@task(groups=meta_session.analysis_grouped, cache_saves="avg_swr_rate_byphase")
def cache_avg_combined_swr_rate_byphase(
    infos, group_name, *, all_task_times, all_swrs_byphase, all_position
):
    return get_combined_swr_rate_byphase(
        all_task_times, all_swrs_byphase, all_position, restonly=True
    )


@task(
    infos=meta_session.all_infos,
    cache_saves=["replay_rate_byphase", "replay_n_byphase"],
)
def cache_replay_rate_byphase(info, *, task_times, replays_byphase, position):
    rates = {}
    n = {}
    for trajectory in meta.trajectories + meta.exclusive_trajectories:
        rates[trajectory], n[trajectory] = get_swr_rate_byphase(
            task_times, replays_byphase[trajectory], position, restonly=False
        )
    return {"replay_rate_byphase": rates, "replay_n_byphase": n}


@task(groups=meta_session.analysis_grouped, cache_saves="swr_rate_byphase")
def cache_combined_swr_rate_byphase(infos, group_name, *, all_swr_rate_byphase):
    return aggregate.combine_with_append(all_swr_rate_byphase)


@task(groups=meta_session.groups, cache_saves="swr_n_byphase")
def cache_combined_swr_n_byphase(infos, group_name, *, all_swr_n_byphase):
    return aggregate.combine_with_sum(all_swr_n_byphase)


@task(groups=meta_session.analysis_grouped, savepath=("swrs", "swrs_n_byphase.tex"))
def save_n_variable_swrs_byphase(infos, group_name, *, all_swr_n_byphase, savepath):
    with open(savepath, "w") as fp:
        print("% Number of SWR events by phase", file=fp)
        total_swrs_n = {task_time: [] for task_time in meta.task_times}
        for info, swrs in zip(infos, all_swr_n_byphase):
            print(f"% {info.session_id}", file=fp)
            for task_time in meta.task_times:
                print(f"% N swrs: {swrs[task_time]}", file=fp)
                total_swrs_n[task_time].append(swrs[task_time])
            print("% ---------", file=fp)

        print("% Combined", file=fp)
        total_swrs = [np.sum(total_swrs_n[task_time]) for task_time in meta.task_times]
        for task_time in meta.task_times:
            phase = meta.tex_ids[task_time]
            print(
                fr"\def \total{phase}swrsn/{{{np.sum(total_swrs_n[task_time])}}}",
                file=fp,
            )
            print(
                fr"\def \total{phase}swrspercent/"
                fr"{{{(np.sum(total_swrs_n[task_time]) / np.sum(total_swrs)) * 100:.1f}}}",
                file=fp,
            )
        print("% ---------", file=fp)


@task(groups=meta_session.analysis_grouped, savepath=("swrs", "swrs_rates_byphase.tex"))
def save_rates_variable_swrs_byphase(
    infos, group_name, *, swr_rate_byphase_restonly, savepath
):
    with open(savepath, "w") as fp:
        print("% SWR rates by phase", file=fp)

        print("% Combined", file=fp)
        for task_time in meta.task_times:
            print(
                fr"\def \total{meta.tex_ids[task_time]}swrsrate/{{{np.mean(swr_rate_byphase_restonly[task_time]) * 60:.2f}}}",
                file=fp,
            )
        print("% ---------", file=fp)


@task(groups=meta_session.groups, cache_saves="replay_n_byphase")
def cache_combined_replay_n_byphase(infos, group_name, *, all_replay_n_byphase):
    return {
        trajectory: aggregate.combine_with_sum(
            [replay_n_byphase[trajectory] for replay_n_byphase in all_replay_n_byphase]
        )
        for trajectory in meta.trajectories + meta.exclusive_trajectories
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=["swr_rate_byphase_restonly", "swr_n_byphase_restonly"],
)
def cache_swr_rate_byphase_restonly(info, *, task_times, swrs_byphase, position):
    rates, n = get_swr_rate_byphase(task_times, swrs_byphase, position, restonly=True)
    return {"swr_rate_byphase_restonly": rates, "swr_n_byphase_restonly": n}


@task(groups=meta_session.groups, cache_saves="swr_rate_byphase_restonly")
def cache_combined_swr_rate_byphase_restonly(
    infos, group_name, *, all_swr_rate_byphase_restonly
):
    return aggregate.combine_with_append(all_swr_rate_byphase_restonly)


@task(groups=meta_session.groups, cache_saves="swr_n_byphase_restonly")
def cache_combined_swr_n_byphase_restonly(
    infos, group_name, *, all_swr_n_byphase_restonly
):
    return aggregate.combine_with_sum(all_swr_n_byphase_restonly)


def get_swrs_bybin(maze_times, linear, swrs_byzone, restonly):
    n_bins = 100
    bin_edges = np.arange(n_bins + 1)
    bin_centers = np.arange(n_bins) + 0.5

    swrs_bybin = {trajectory: np.zeros(n_bins) for trajectory in swrs_byzone}
    occupancy = {}
    rate_bybin = {}
    for trajectory in meta.trajectories + meta.exclusive_trajectories:
        if trajectory not in swrs_byzone:
            continue

        if trajectory == "both":
            continue
        elif trajectory.startswith("only_"):
            this_linear = linear[trajectory[len("only_") :]]
        else:
            this_linear = linear[trajectory]

        dt = np.median(np.diff(this_linear.time))
        if restonly:
            this_linear = this_linear[
                nept.rest_threshold(
                    this_linear,
                    thresh=meta.std_rest_limit,
                    t_smooth=meta.t_smooth,
                )
            ]

        this_swrs_byzone = swrs_byzone[trajectory].intersect(maze_times)

        for swr in this_swrs_byzone.centers:
            time_idx = nept.find_nearest_idx(this_linear.time, swr)
            # If we don't have a real time we're not in a real point so don't count this SWR
            if abs(this_linear.time[time_idx] - swr) > 1:
                continue
            idx = nept.find_nearest_idx(bin_centers, this_linear.x[time_idx])
            swrs_bybin[trajectory][idx] += 1

        this_occupancy, _ = np.histogram(this_linear.x, bins=bin_edges)
        occupancy[trajectory] = this_occupancy * dt

        this_rate_bybin = swrs_bybin[trajectory] / occupancy[trajectory]
        this_rate_bybin[np.isinf(this_rate_bybin)] = 0
        this_rate_bybin[np.isnan(this_rate_bybin)] = 0
        rate_bybin[trajectory] = this_rate_bybin
    return swrs_bybin, occupancy, rate_bybin


@task(
    infos=meta_session.all_infos,
    cache_saves=["swrs_bybin", "swr_occupancy_bybin", "swr_rate_bybin"],
)
def cache_swrs_bybin(info, *, task_times, linear, swrs_byzone):
    swrs_bybin, occupancy, rate_bybin = get_swrs_bybin(
        task_times["maze_times"], linear, swrs_byzone, restonly=False
    )
    return {
        "swrs_bybin": swrs_bybin,
        "swr_occupancy_bybin": occupancy,
        "swr_rate_bybin": rate_bybin,
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=[
        "swrs_bybin_restonly",
        "swr_occupancy_bybin_restonly",
        "swr_rate_bybin_restonly",
    ],
)
def cache_swrs_bybin_restonly(info, *, task_times, linear, swrs_byzone):
    swrs_bybin, occupancy, rate_bybin = get_swrs_bybin(
        task_times["maze_times"], linear, swrs_byzone, restonly=True
    )
    return {
        "swrs_bybin_restonly": swrs_bybin,
        "swr_occupancy_bybin_restonly": occupancy,
        "swr_rate_bybin_restonly": rate_bybin,
    }


@task(infos=meta_session.all_infos, cache_saves=["replays_bybin", "replay_rate_bybin"])
def cache_replays_bybin(info, *, task_times, linear, replays):
    replays_bybin, _, rate_bybin = get_swrs_bybin(
        task_times["maze_times"], linear, replays, restonly=False
    )
    return {
        "replays_bybin": replays_bybin,
        "replay_rate_bybin": rate_bybin,
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=["matched_replays_bybin", "matched_replay_rate_bybin"],
)
def cache_matched_replays_bybin(info, *, task_times, matched_linear, replays):
    replays_bybin, _, rate_bybin = get_swrs_bybin(
        task_times["maze_times"], matched_linear, replays, restonly=False
    )
    return {
        "matched_replays_bybin": replays_bybin,
        "matched_replay_rate_bybin": rate_bybin,
    }


def combine_with_nansum(values_bygroup, axis=0):
    return {
        group: np.nansum(values_bygroup[group], axis=axis) for group in values_bygroup
    }


def combine_with_nanmean(values_bygroup, axis=0):
    return {
        group: np.nanmean(values_bygroup[group], axis=axis) for group in values_bygroup
    }


@task(groups=meta_session.groups, cache_saves="swrs_bybin")
def cache_combined_swrs_bybin(infos, group_name, *, all_swrs_bybin):
    return combine_with_nansum(aggregate.combine_with_append(all_swrs_bybin))


@task(groups=meta_session.groups, cache_saves="swrs_bybin_restonly")
def cache_combined_swrs_bybin_restonly(infos, group_name, *, all_swrs_bybin_restonly):
    return combine_with_nansum(aggregate.combine_with_append(all_swrs_bybin_restonly))


@task(groups=meta_session.groups, cache_saves="swr_rate_bybin")
def cache_combined_swr_rate_bybin(infos, group_name, *, all_swr_rate_bybin):
    return combine_with_nanmean(aggregate.combine_with_append(all_swr_rate_bybin))


@task(groups=meta_session.groups, cache_saves="swr_rate_bybin_restonly")
def cache_combined_swr_rate_bybin_restonly(
    infos, group_name, *, all_swr_rate_bybin_restonly
):
    return combine_with_nanmean(
        aggregate.combine_with_append(all_swr_rate_bybin_restonly)
    )


@task(groups=meta_session.groups, cache_saves="swr_occupancy_bybin")
def cache_combined_swr_occupancy_bybin(infos, group_name, *, all_swr_occupancy_bybin):
    return combine_with_nanmean(aggregate.combine_with_append(all_swr_occupancy_bybin))


@task(groups=meta_session.groups, cache_saves="swr_occupancy_bybin_restonly")
def cache_combined_swr_occupancy_bybin_restonly(
    infos, group_name, *, all_swr_occupancy_bybin_restonly
):
    return combine_with_nanmean(
        aggregate.combine_with_append(all_swr_occupancy_bybin_restonly)
    )


@task(groups=meta_session.groups, cache_saves="replays_bybin")
def cache_combined_replays_bybin(infos, group_name, *, all_replays_bybin):
    return combine_with_nansum(aggregate.combine_with_append(all_replays_bybin))


@task(groups=meta_session.groups, cache_saves="matched_replays_bybin")
def cache_combined_matched_replays_bybin(
    infos, group_name, *, all_matched_replays_bybin
):
    return combine_with_nansum(aggregate.combine_with_append(all_matched_replays_bybin))


@task(groups=meta_session.groups, cache_saves="replay_rate_bybin")
def cache_combined_replay_rate_bybin(infos, group_name, *, all_replay_rate_bybin):
    return combine_with_nanmean(aggregate.combine_with_append(all_replay_rate_bybin))


def bin_swr_events(swrs, bin_edges):
    return nept.AnalogSignal(
        np.histogram(swrs.centers, bins=bin_edges)[0].astype(float),
        bin_edges[:-1],
    )


@task(infos=meta_session.all_infos, cache_saves="swrs_overtime")
def cache_swrs_overtime(info, *, task_times, swrs):
    bin_edges = nept.get_edges(
        task_times["prerecord"].start,
        task_times["postrecord"].stop,
        meta.swr_overtime_dt,
        lastbin=False,
    )
    return bin_swr_events(swrs, bin_edges)


@task(infos=meta_session.all_infos, cache_saves="replays_overtime")
def cache_replays_overtime(info, *, task_times, replays):
    dt = 30  # TODO: add swr_overtime_dt to meta?
    bin_edges = nept.get_edges(
        task_times["prerecord"].start,
        task_times["postrecord"].stop,
        dt,
        lastbin=False,
    )
    return {
        trajectory: bin_swr_events(replays[trajectory], bin_edges)
        for trajectory in replays
    }


def get_swr_in_position(swr_maze_times, position):
    idx = []
    for center in swr_maze_times.centers:
        idx.append(nept.find_nearest_idx(position.time, center))
    return position[idx]


@task(infos=meta_session.all_infos, cache_saves="swr_in_position")
def cache_swr_in_position(info, *, task_times, position, swrs):
    return get_swr_in_position(
        swrs.intersect(task_times["maze_times"]), position[task_times["maze_times"]]
    )


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        trajectory: ("swrs", f"swrs_near_feeders_{trajectory}.tex")
        for trajectory in meta.trajectories
    },
)
def save_swrs_near_feeders(
    infos, group_name, *, all_task_times, all_swrs, all_swrs_byzone, savepath
):
    for trajectory in meta.trajectories:
        traj = trajectory.replace("_", "")
        feeders = [f"{trajectory}_feeder1", f"{trajectory}_feeder2"]
        with open(savepath[trajectory], "w") as fp:
            print(f"% Number of SWR events by feeders for {trajectory}", file=fp)
            combined = {feeder: 0 for feeder in feeders}
            total = 0
            for info, task_times, swrs, swrs_byzone in zip(
                infos, all_task_times, all_swrs, all_swrs_byzone
            ):
                swrs_maze_byzone = {feeder: [] for feeder in feeders}
                swr_maze_times = swrs.intersect(task_times["maze_times"])
                total += swr_maze_times.n_epochs
                print(f"% {info.session_id}", file=fp)
                for feeder in feeders:
                    swrs_maze_byzone[feeder] = swrs_byzone[feeder].intersect(
                        task_times["maze_times"]
                    )
                    n_by_feeder = swrs_maze_byzone[feeder].n_epochs
                    print(
                        f"% {feeder}: {n_by_feeder} / {swr_maze_times.n_epochs} "
                        f"({(n_by_feeder / swr_maze_times.n_epochs) * 100:.1f}%)",
                        file=fp,
                    )
                    combined[feeder] += swrs_maze_byzone[feeder].n_epochs
                print("% -------\n", file=fp)
            print("% Combined", file=fp)
            both_feeders = [combined[feeder] for feeder in feeders]
            for feeder in feeders:
                print(
                    f"% {feeder}: {combined[feeder]} / {total} "
                    f"% ({combined[feeder] / total:.4f})",
                    file=fp,
                )
            print(
                fr"\def \swrsbyfeedersn{traj}/{{{sum(both_feeders)}}}",
                file=fp,
            )
            print(
                fr"\def \swrstotalmazen{traj}/{{{total}}}",
                file=fp,
            )
            print(
                fr"\def \swrsbyfeederspercent{traj}/{{{(sum(both_feeders)/total)*100:.1f}}}",
                file=fp,
            )


@task(groups=meta_session.analysis_grouped, savepath=("replays", "n_replays.table"))
def save_replays(infos, group_name, *, all_replays_byphase, savepath):
    with open(savepath, "w") as fp:
        print(
            r"""
            \begin{tabular}{c | c c c c c c c}
 \toprule
 \textbf{Rat~ID} & \textbf{Pre-task} & \textbf{Phase~1} & \textbf{Pause~A} & \textbf{Phase~2} &
 \textbf{Pause~B} & \textbf{Phase~3} & \textbf{Post-task} \\ [0.5ex]
 \midrule
 """.strip(),
            file=fp,
        )
        u_totals = [0 for _ in range(len(meta.task_times))]
        shortcut_totals = [0 for _ in range(len(meta.task_times))]
        for info, replays_byphase in zip(infos, all_replays_byphase):
            output = rf"\textbf{{{info.session_id}}} "
            for i, phase in enumerate(meta.task_times):
                u_replays = replays_byphase["u"][phase].n_epochs
                shortcut_replays = replays_byphase["full_shortcut"][phase].n_epochs
                output = (
                    output
                    + rf"& \textbf{{{u_replays + shortcut_replays}}} "
                    + rf"({u_replays} $\mid$ {shortcut_replays}) "
                )
                u_totals[i] += u_replays
                shortcut_totals[i] += shortcut_replays

            space = " [1ex]" if info.session_id == "R068d8" else ""
            print(
                rf"{output} \\{space}",
                file=fp,
            )
            if info.session_id in ["R063d8", "R066d8", "R067d8"]:
                print(r"\midrule", file=fp)

        output = r"\textbf{{Total}} "
        for i, phase in enumerate(meta.task_times):
            output = (
                output + rf"& \textbf{{{u_totals[i] + shortcut_totals[i]}}} "
                rf"({u_totals[i]} $\mid$ {shortcut_totals[i]}) "
            )
        print(r"\bottomrule", file=fp)
        print(
            rf"{output} \\",
            file=fp,
        )
        print(r"\bottomrule", file=fp)
        print(r"\end{tabular}", file=fp)


@task(
    groups=meta_session.analysis_grouped, savepath=("replays", "percent_replays.table")
)
def save_replays_percents(
    infos, group_name, *, all_replays_byphase, all_swrs_byphase, savepath
):
    with open(savepath, "w") as fp:
        print(
            r"""
            \begin{tabular}{c | c c c c c c c}
 \toprule
 \textbf{Rat~ID} & \textbf{Pre-task} & \textbf{Phase~1} & \textbf{Pause~A} & \textbf{Phase~2} &
 \textbf{Pause~B} & \textbf{Phase~3} & \textbf{Post-task} \\ [0.5ex]
 \midrule
 """.strip(),
            file=fp,
        )
        u_totals = [0 for _ in range(len(meta.task_times))]
        shortcut_totals = [0 for _ in range(len(meta.task_times))]
        for info, replays_byphase, swrs_byphase in zip(
            infos, all_replays_byphase, all_swrs_byphase
        ):
            output = rf"\textbf{{{info.session_id}}} "
            for i, phase in enumerate(meta.task_times):
                u_replays = replays_byphase["u"][phase].n_epochs
                shortcut_replays = replays_byphase["full_shortcut"][phase].n_epochs

                percent_together = (
                    f"{(u_replays + shortcut_replays) / swrs_byphase[phase].n_epochs * 100:.1f}"
                    if swrs_byphase[phase].n_epochs > 0
                    else "-"
                )

                output = output + rf"& {percent_together} "
                u_totals[i] += u_replays
                shortcut_totals[i] += shortcut_replays

            space = " [1ex]" if info.session_id == "R068d8" else ""
            print(
                rf"{output} \\{space}",
                file=fp,
            )
            if info.session_id in ["R063d8", "R066d8", "R067d8"]:
                print(r"\midrule", file=fp)

        output = r"\textbf{{Total}} "
        for i, phase in enumerate(meta.task_times):
            total_swrs = np.sum(
                [swrs_byphase[phase].n_epochs for swrs_byphase in all_swrs_byphase]
            )
            percent_together = (u_totals[i] + shortcut_totals[i]) / total_swrs * 100
            output = output + rf"& \textbf{{{percent_together:.1f}}} "
        print(r"\bottomrule", file=fp)
        print(
            rf"{output} \\",
            file=fp,
        )
        print(r"\bottomrule", file=fp)
        print(r"\end{tabular}", file=fp)


@task(groups=meta_session.analysis_grouped, savepath=("replays", "replays_byphase.tex"))
def save_replays_byphase(
    infos, group_name, *, all_swrs_byphase, all_replays_byphase, savepath
):
    with open(savepath, "w") as fp:
        print("% Replays byphase\n", file=fp)
        total_n_replays = {
            trajectory: {phase: 0 for phase in meta.task_times}
            for trajectory in meta.trajectories
        }
        total_n_swrs = {phase: 0 for phase in meta.task_times}
        for info, swrs_byphase, replays_byphase in zip(
            infos, all_swrs_byphase, all_replays_byphase
        ):
            for trajectory in meta.trajectories:
                for phase in meta.task_times:
                    total_n_replays[trajectory][phase] += replays_byphase[trajectory][
                        phase
                    ].n_epochs
                    if trajectory == "u":
                        total_n_swrs[phase] += swrs_byphase[phase].n_epochs
        print("% ---------\n", file=fp)
        print("% Combined", file=fp)

        allphases_swrs = [np.sum(total_n_swrs[phase]) for phase in meta.task_times]
        pedestal_swrs = [np.sum(total_n_swrs[phase]) for phase in meta.rest_times]
        maze_swrs = [np.sum(total_n_swrs[phase]) for phase in meta.run_times]
        for trajectory in meta.trajectories:
            traj = trajectory.replace("_", "")
            print(f"% {trajectory}", file=fp)
            for phase in meta.task_times:
                print(
                    f"% {phase}: {total_n_replays[trajectory][phase]} / {total_n_swrs[phase]} "
                    f"({(total_n_replays[trajectory][phase] / total_n_swrs[phase]) * 100:.1f})",
                    file=fp,
                )
            allphases_replays = [
                np.sum(total_n_replays[trajectory][phase]) for phase in meta.task_times
            ]
            print(
                fr"\def \all{traj}replayn/{{{sum(allphases_replays)}}}",
                file=fp,
            )
            print(
                fr"\def \all{traj}replaypercent/{{{(sum(allphases_replays) / sum(allphases_swrs)) * 100:.1f}}}",
                file=fp,
            )
            pedestal_replays = [
                np.sum(total_n_replays[trajectory][phase]) for phase in meta.rest_times
            ]

            print(
                fr"\def \pedestal{traj}replayn/{{{sum(pedestal_replays)}}}",
                file=fp,
            )
            print(
                fr"\def \pedestal{traj}replaypercent/{{{(sum(pedestal_replays) / sum(pedestal_swrs)) * 100:.1f}}}",
                file=fp,
            )
            maze_replays = [
                np.sum(total_n_replays[trajectory][phase]) for phase in meta.run_times
            ]
            print(
                fr"\def \maze{traj}replayn/{{{sum(maze_replays)}}}",
                file=fp,
            )
            print(
                fr"\def \maze{traj}replaypercent/{{{(sum(maze_replays) / sum(maze_swrs)) * 100:.1f}}}",
                file=fp,
            )


@task(groups=meta_session.groups, savepath=("replays", "n_replays.tex"))
def save_n_replays(infos, group_name, *, all_replays_byphase, savepath):
    total_u_replays = 0
    total_shortcut_replays = 0
    with open(savepath, "w") as fp:
        for info, replays_byphase in zip(infos, all_replays_byphase):
            u_replays = 0
            shortcut_replays = 0
            print(f"% {info.session_id}", file=fp)
            for i, phase in enumerate(meta.task_times):
                u_replays += replays_byphase["u"][phase].n_epochs
                shortcut_replays += replays_byphase["full_shortcut"][phase].n_epochs
            total_u_replays += u_replays
            total_shortcut_replays += shortcut_replays
            print(f"% Total replays: {u_replays + shortcut_replays}", file=fp)
            print(f"% Familiar replays: {u_replays}", file=fp)
            print(f"% Shortcut replays: {shortcut_replays}", file=fp)
            print("% ---------\n", file=fp)
        print("% Combined", file=fp)
        print(
            fr"\def \{meta.tex_ids[group_name]}replayun/{{{total_u_replays}}}",
            file=fp,
        )
        print(
            fr"\def \{meta.tex_ids[group_name]}replayfullshortcutn/{{{total_shortcut_replays}}}",
            file=fp,
        )
        print(
            fr"\def \{meta.tex_ids[group_name]}replaycombinedn/{{{total_u_replays + total_shortcut_replays}}}",
            file=fp,
        )


@task(
    groups=meta_session.analysis_grouped,
    savepath=("replays", "replays_mean_durations.tex"),
)
def save_replays_mean_durations(infos, group_name, *, all_replays_byphase, savepath):
    replays_durations = {trajectory: [] for trajectory in meta.exclusive_trajectories}
    for info, replays_byphase in zip(infos, all_replays_byphase):
        for trajectory in meta.exclusive_trajectories:
            for phase in meta.task_times:
                replays_durations[trajectory].extend(
                    replays_byphase[trajectory][phase].durations
                )
    with open(savepath, "w") as fp:
        print("% Combined replay durations", file=fp)
        for trajectory in meta.exclusive_trajectories:
            traj = trajectory.replace("_", "")
            mean_duration = np.mean(replays_durations[trajectory]) * 1000
            print(
                fr"\def \{traj}replaymeandurations/{{{mean_duration:.1f}}}",
                file=fp,
            )


def get_replay_proportions_byphase(swr_n_byphase, replay_n_byphase):
    replay_proportion = {}
    for trajectory in replay_n_byphase:
        replay_proportion[trajectory] = {}
        for phase in meta.task_times:
            replay_proportion[trajectory][phase] = (
                replay_n_byphase[trajectory][phase] / swr_n_byphase[phase]
                if swr_n_byphase[phase] > 0
                else 0
            )
    replay_proportion["difference"] = {
        phase: replay_proportion["only_full_shortcut"][phase]
        - replay_proportion["only_u"][phase]
        for phase in meta.task_times
    }
    exclusive_sum = {
        phase: replay_proportion["only_full_shortcut"][phase]
        + replay_proportion["only_u"][phase]
        for phase in meta.task_times
    }
    replay_proportion["contrast"] = {
        phase: replay_proportion["difference"][phase] / exclusive_sum[phase]
        if exclusive_sum[phase] > 0
        else 0
        for phase in meta.task_times
    }

    return replay_proportion


@task(infos=meta_session.all_infos, cache_saves="replay_proportions_byphase")
def cache_replay_proportions_byphase(info, *, swr_n_byphase, replay_n_byphase):
    return get_replay_proportions_byphase(swr_n_byphase, replay_n_byphase)


@task(groups=meta_session.groups, cache_saves="replay_proportions_byphase")
def cache_combined_replay_proportions_byphase(
    infos, group_name, *, swr_n_byphase, replay_n_byphase
):
    return get_replay_proportions_byphase(swr_n_byphase, replay_n_byphase)


def get_replay_proportions_byphase_pval(swr_n_byphase, replay_n_byphase):
    pval = {}
    for trajectory in replay_n_byphase:
        pval[trajectory] = {}
        for left, right in zip(
            meta.rest_times[:-1] + meta.run_times[:-1],
            meta.rest_times[1:] + meta.run_times[1:],
        ):
            pval[trajectory][(left, right)] = (
                ranksum_test(
                    xtotal=swr_n_byphase[left],
                    xn=replay_n_byphase[trajectory][left],
                    ytotal=swr_n_byphase[right],
                    yn=replay_n_byphase[trajectory][right],
                )
                if swr_n_byphase[left] > 0 and swr_n_byphase[right] > 0
                else 1.0
            )

    for key in ["overlapping", "exclusive"]:
        prefix = "only_" if key == "exclusive" else ""
        pval[key] = {
            task_time: ranksum_test(
                xtotal=swr_n_byphase[task_time],
                xn=replay_n_byphase[f"{prefix}u"][task_time],
                ytotal=swr_n_byphase[task_time],
                yn=replay_n_byphase[f"{prefix}full_shortcut"][task_time],
            )
            if swr_n_byphase[task_time] > 0
            else 1.0
            for task_time in meta.task_times
        }

    return pval


@task(infos=meta_session.all_infos, cache_saves="replay_proportions_byphase_pval")
def cache_replay_proportions_byphase_pval(info, *, swr_n_byphase, replay_n_byphase):
    return get_replay_proportions_byphase_pval(swr_n_byphase, replay_n_byphase)


@task(groups=meta_session.groups, cache_saves="replay_proportions_byphase_pval")
def cache_combined_replay_proportions_byphase_pval(
    infos, group_name, *, swr_n_byphase, replay_n_byphase
):
    return get_replay_proportions_byphase_pval(swr_n_byphase, replay_n_byphase)


@task(groups=meta_session.analysis_grouped, cache_saves="replay_proportions_byphase_df")
def cache_replay_proportions_byphase_df(
    infos, group_name, *, replay_proportions_byphase
):
    replay_proportions_byphase_df = []
    for trajectory in meta.trajectories:
        replay_proportions_byphase_df.extend(
            {
                "proportions": replay_proportions_byphase[trajectory][phase],
                "phase": phase,
                "trajectory": trajectory,
            }
            for phase in meta.task_times
        )
    return pd.DataFrame.from_dict(replay_proportions_byphase_df)


@task(
    groups=meta_session.analysis_grouped,
    savepath=("replays", "stats_replay_proportions_byphase.tex"),
)
def save_replay_proportions_byphase_statsmodel(
    infos, group_name, *, replay_proportions_byphase_df, savepath
):
    model = smf.mixedlm(
        "proportions ~ trajectory",
        replay_proportions_byphase_df,
        groups=replay_proportions_byphase_df["phase"],
    )
    modelfit = model.fit()
    summary = str(modelfit.summary()).split("\n")
    with open(savepath, "w") as fp:
        print("% Stats replay_proportions_byphase\n", file=fp)
        for output in summary:
            print(f"% {output}", file=fp)


@task(groups=meta_session.groups, cache_saves="replay_proportions_normalized_byphase")
def cache_replay_proportions_normalized_byphase(
    infos, group_name, *, replay_proportions_byphase
):
    normalized = {}
    for trajectory in replay_proportions_byphase:
        if trajectory in ["difference", "contrast"]:
            continue
        proportions = np.array(list(replay_proportions_byphase[trajectory].values()))
        proportions /= np.mean(proportions)
        normalized[trajectory] = {
            phase: proportions[i]
            for i, phase in enumerate(replay_proportions_byphase[trajectory])
        }
    return normalized


def get_swrs_byexperience_bytrial(trials, swrs):
    first_shortcut_trial = trials["full_shortcut"][0]
    shortcut_trials = trials["full_shortcut"][1:]
    familiar_trials = trials["u"].time_slice(
        first_shortcut_trial.stop, trials["u"].stop
    )

    return {
        "familiar_phase12": (swrs["phase1"].n_epochs + swrs["phase2"].n_epochs),
        "first_shortcut": (swrs["phase3"].intersect(first_shortcut_trial).n_epochs),
        "shortcut_phase3": (swrs["phase3"].intersect(shortcut_trials).n_epochs),
        "familiar_phase3": (swrs["phase3"].intersect(familiar_trials).n_epochs),
    }


def get_swrs_byexperience(task_times, trials, swrs):
    first_shortcut_trial = trials["full_shortcut"][0]
    phase3_after = nept.Epoch(first_shortcut_trial.stop, task_times["phase3"].stop)

    return {
        "familiar_phase12": (swrs["phase1"].n_epochs + swrs["phase2"].n_epochs),
        "first_shortcut": (swrs["phase3"].intersect(first_shortcut_trial).n_epochs),
        "phase3_after": (swrs["phase3"].intersect(phase3_after).n_epochs),
    }


@task(infos=meta_session.all_infos, cache_saves="swr_n_byexperience_bytrial")
def cache_swr_n_byexperience_bytrial(info, *, task_times, trials, swrs_byphase):
    return get_swrs_byexperience_bytrial(trials, swrs_byphase)


@task(groups=meta_session.groups, cache_saves="swr_n_byexperience_bytrial")
def cache_combined_swr_n_byexperience_bytrial(
    infos, group_name, *, all_swr_n_byexperience_bytrial
):
    return {
        experience: sum(
            swr_n_byexperience[experience]
            for swr_n_byexperience in all_swr_n_byexperience_bytrial
        )
        for experience in meta.experiences
    }


@task(infos=meta_session.all_infos, cache_saves="swr_n_byexperience")
def cache_swr_n_byexperience(info, *, task_times, trials, swrs_byphase):
    return get_swrs_byexperience(task_times, trials, swrs_byphase)


@task(groups=meta_session.groups, cache_saves="swr_n_byexperience")
def cache_combined_swr_n_byexperience(infos, group_name, *, all_swr_n_byexperience):
    return {
        experience: sum(
            swr_n_byexperience[experience]
            for swr_n_byexperience in all_swr_n_byexperience
        )
        for experience in meta.on_task
    }


@task(infos=meta_session.all_infos, cache_saves="replay_n_byexperience_bytrial")
def cache_replay_n_byexperience_bytrial(info, *, trials, replays_byphase):
    first_shortcut_trial = trials["full_shortcut"][0]
    shortcut_trials = trials["full_shortcut"][1:]
    familiar_trials = trials["u"].time_slice(
        first_shortcut_trial.stop, trials["u"].stop
    )

    return {
        trajectory: {
            "familiar_phase12": (
                replays_byphase[trajectory]["phase1"].n_epochs
                + replays_byphase[trajectory]["phase2"].n_epochs
            ),
            "first_shortcut": (
                replays_byphase[trajectory]["phase3"]
                .intersect(first_shortcut_trial)
                .n_epochs
            ),
            "shortcut_phase3": (
                replays_byphase[trajectory]["phase3"]
                .intersect(shortcut_trials)
                .n_epochs
            ),
            "familiar_phase3": (
                replays_byphase[trajectory]["phase3"]
                .intersect(familiar_trials)
                .n_epochs
            ),
        }
        for trajectory in replays_byphase
    }


@task(groups=meta_session.groups, cache_saves="replay_n_byexperience_bytrial")
def cache_combined_replay_n_byexperience_bytrial(
    infos, group_name, *, all_replay_n_byexperience_bytrial
):
    return {
        trajectory: {
            experience: sum(
                replay_n_byexperience[trajectory][experience]
                for replay_n_byexperience in all_replay_n_byexperience_bytrial
            )
            for experience in meta.experiences
        }
        for trajectory in all_replay_n_byexperience_bytrial[0]
    }


@task(infos=meta_session.all_infos, cache_saves="replay_n_byexperience")
def cache_replay_n_byexperience(info, *, task_times, trials, replays_byphase):
    first_shortcut_trial = trials["full_shortcut"][0]
    phase3_after = nept.Epoch(first_shortcut_trial.stop, task_times["phase3"].stop)

    return {
        trajectory: {
            "familiar_phase12": (
                replays_byphase[trajectory]["phase1"].n_epochs
                + replays_byphase[trajectory]["phase2"].n_epochs
            ),
            "first_shortcut": (
                replays_byphase[trajectory]["phase3"]
                .intersect(first_shortcut_trial)
                .n_epochs
            ),
            "phase3_after": (
                replays_byphase[trajectory]["phase3"].intersect(phase3_after).n_epochs
            ),
        }
        for trajectory in replays_byphase
    }


@task(groups=meta_session.groups, cache_saves="replay_n_byexperience")
def cache_combined_replay_n_byexperience(
    infos, group_name, *, all_replay_n_byexperience
):
    return {
        trajectory: {
            experience: sum(
                replay_n_byexperience[trajectory][experience]
                for replay_n_byexperience in all_replay_n_byexperience
            )
            for experience in meta.on_task
        }
        for trajectory in all_replay_n_byexperience[0]
    }


def get_replay_proportions_byexperience_bytrial(replay_n, swr_n):
    prop = {
        trajectory: {
            experience: replay_n[trajectory][experience] / swr_n[experience]
            if swr_n[experience] > 0
            else 0
            for experience in meta.experiences
        }
        for trajectory in replay_n
    }
    prop["difference"] = {
        experience: prop["only_full_shortcut"][experience] - prop["only_u"][experience]
        for experience in meta.experiences
    }
    exclusive_sum = {
        experience: prop["only_full_shortcut"][experience] + prop["only_u"][experience]
        for experience in meta.experiences
    }
    prop["contrast"] = {
        experience: prop["difference"][experience] / exclusive_sum[experience]
        if exclusive_sum[experience] > 0
        else 0
        for experience in meta.experiences
    }
    return prop


def get_replay_proportions_byexperience(replay_n, swr_n):
    prop = {
        trajectory: {
            experience: replay_n[trajectory][experience] / swr_n[experience]
            if swr_n[experience] > 0
            else 0
            for experience in meta.on_task
        }
        for trajectory in replay_n
    }
    prop["difference"] = {
        experience: prop["only_full_shortcut"][experience] - prop["only_u"][experience]
        for experience in meta.on_task
    }
    exclusive_sum = {
        experience: prop["only_full_shortcut"][experience] + prop["only_u"][experience]
        for experience in meta.on_task
    }
    prop["contrast"] = {
        experience: prop["difference"][experience] / exclusive_sum[experience]
        if exclusive_sum[experience] > 0
        else 0
        for experience in meta.on_task
    }
    return prop


@task(
    infos=meta_session.all_infos, cache_saves="replay_proportions_byexperience_bytrial"
)
def cache_replay_proportions_byexperience_bytrial(
    info, *, replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
):
    return get_replay_proportions_byexperience_bytrial(
        replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
    )


@task(groups=meta_session.groups, cache_saves="replay_proportions_byexperience_bytrial")
def cache_combined_replay_proportions_byexperience_bytrial(
    infos, group_name, *, replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
):
    return get_replay_proportions_byexperience_bytrial(
        replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
    )


def get_replay_proportions_byexperience_pval(replay_n, swr_n):
    return {
        key: {
            task_time: ranksum_test(
                xtotal=swr_n[task_time],
                xn=replay_n[f"{'only_' if key == 'exclusive' else ''}u"][task_time],
                ytotal=swr_n[task_time],
                yn=replay_n[f"{'only_' if key == 'exclusive' else ''}full_shortcut"][
                    task_time
                ],
            )
            if swr_n[task_time] > 0
            else 1.0
            for task_time in meta.on_task
        }
        for key in ["overlapping", "exclusive"]
    }


def get_replay_proportions_byexperience_bytrial_pval(replay_n, swr_n):
    return {
        key: {
            task_time: ranksum_test(
                xtotal=swr_n[task_time],
                xn=replay_n[f"{'only_' if key == 'exclusive' else ''}u"][task_time],
                ytotal=swr_n[task_time],
                yn=replay_n[f"{'only_' if key == 'exclusive' else ''}full_shortcut"][
                    task_time
                ],
            )
            if swr_n[task_time] > 0
            else 1.0
            for task_time in meta.experiences
        }
        for key in ["overlapping", "exclusive"]
    }


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_bytrial_pval",
)
def cache_replay_proportions_byexperience_bytrial_pval(
    info, *, replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
):
    return get_replay_proportions_byexperience_pval(
        replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_bytrial_pval",
)
def cache_combined_replay_proportions_byexperience_bytrial_pval(
    infos, group_name, *, replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
):
    return get_replay_proportions_byexperience_bytrial_pval(
        replay_n_byexperience_bytrial, swr_n_byexperience_bytrial
    )


@task(infos=meta_session.all_infos, cache_saves="swrs_byphase_feederonly")
def cache_swrs_byphase_feederonly(info, *, position_byzone, swrs_byphase):
    swrs_infeeders = {phase: [] for phase in meta.run_times}
    for phase in meta.run_times:
        starts = []
        stops = []
        for swr in swrs_byphase[phase]:
            for feeder in [
                "u_feeder1",
                "u_feeder2",
                "full_shortcut_feeder1",
                "full_shortcut_feeder2",
            ]:
                feeder_time = position_byzone[feeder].time
                if swr.starts not in starts:
                    if np.allclose(
                        swr.centers,
                        feeder_time[
                            nept.find_nearest_idx(
                                position_byzone[feeder].time, swr.centers
                            )
                        ],
                    ):
                        starts.append(swr.start)
                        stops.append(swr.stop)
        if len(starts) > 0:
            swrs_infeeders[phase] = nept.Epoch(starts, stops)
        else:
            swrs_infeeders[phase] = nept.Epoch([], [])
    return swrs_infeeders


@task(infos=meta_session.all_infos, cache_saves="swr_n_byexperience_feederonly_bytrial")
def cache_swr_n_byexperience_feederonly_bytrial(
    info, *, trials, swrs_byphase_feederonly
):
    return get_swrs_byexperience_bytrial(trials, swrs_byphase_feederonly)


@task(groups=meta_session.groups, cache_saves="swr_n_byexperience_feederonly_bytrial")
def cache_combined_swr_n_byexperience_feederonly_bytrial(
    infos, group_name, *, all_swr_n_byexperience_feederonly_bytrial
):
    return {
        experience: sum(
            swr_n_byexperience[experience]
            for swr_n_byexperience in all_swr_n_byexperience_feederonly_bytrial
        )
        for experience in meta.experiences
    }


@task(infos=meta_session.all_infos, cache_saves="replays_byphase_feederonly")
def cache_replays_byphase_feederonly(info, *, position_byzone, replays_byphase):
    replays_infeeders = {
        trajectory: {phase: [] for phase in meta.run_times}
        for trajectory in replays_byphase.keys()
    }
    for trajectory in replays_byphase.keys():
        for phase in meta.run_times:
            starts = []
            stops = []
            for replay in replays_byphase[trajectory][phase]:
                for feeder in [
                    "u_feeder1",
                    "u_feeder2",
                    "full_shortcut_feeder1",
                    "full_shortcut_feeder2",
                ]:
                    feeder_time = position_byzone[feeder].time
                    if replay.starts not in starts:
                        if np.allclose(
                            replay.centers,
                            feeder_time[
                                nept.find_nearest_idx(feeder_time, replay.centers)
                            ],
                        ):
                            starts.append(replay.start)
                            stops.append(replay.stop)
            if len(starts) > 0:
                replays_infeeders[trajectory][phase] = nept.Epoch(starts, stops)
            else:
                replays_infeeders[trajectory][phase] = nept.Epoch([], [])
    return replays_infeeders


def get_replays_byexperience(task_times, trials, replays):
    first_shortcut_trial = trials["full_shortcut"][0]
    phase3_after = nept.Epoch(first_shortcut_trial.stop, task_times["phase3"].stop)

    return {
        trajectory: {
            "familiar_phase12": (
                replays[trajectory]["phase1"].n_epochs
                + replays[trajectory]["phase2"].n_epochs
            ),
            "first_shortcut": (
                replays[trajectory]["phase3"].intersect(first_shortcut_trial).n_epochs
            ),
            "phase3_after": (
                replays[trajectory]["phase3"].intersect(phase3_after).n_epochs
            ),
        }
        for trajectory in replays
    }


def get_replays_byexperience_bytrial(trials, replays):
    first_shortcut_trial = trials["full_shortcut"][0]
    shortcut_trials = trials["full_shortcut"][1:]
    familiar_trials = trials["u"].time_slice(
        first_shortcut_trial.stop, trials["u"].stop
    )

    return {
        trajectory: {
            "familiar_phase12": (
                replays[trajectory]["phase1"].n_epochs
                + replays[trajectory]["phase2"].n_epochs
            ),
            "first_shortcut": (
                replays[trajectory]["phase3"].intersect(first_shortcut_trial).n_epochs
            ),
            "shortcut_phase3": (
                replays[trajectory]["phase3"].intersect(shortcut_trials).n_epochs
            ),
            "familiar_phase3": (
                replays[trajectory]["phase3"].intersect(familiar_trials).n_epochs
            ),
        }
        for trajectory in replays
    }


@task(
    infos=meta_session.all_infos, cache_saves="replay_n_byexperience_feederonly_bytrial"
)
def cache_replay_n_byexperience_feederonly_bytrial(
    info, *, trials, replays_byphase_feederonly
):
    return get_replays_byexperience_bytrial(trials, replays_byphase_feederonly)


@task(
    groups=meta_session.groups, cache_saves="replay_n_byexperience_feederonly_bytrial"
)
def cache_combined_replay_n_byexperience_feederonly_bytrial(
    infos, group_name, *, all_replay_n_byexperience_feederonly_bytrial
):
    return {
        trajectory: {
            experience: sum(
                replay_n_byexperience[trajectory][experience]
                for replay_n_byexperience in all_replay_n_byexperience_feederonly_bytrial
            )
            for experience in meta.experiences
        }
        for trajectory in all_replay_n_byexperience_feederonly_bytrial[0]
    }


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_feederonly_bytrial",
)
def cache_replay_proportions_byexperience_feederonly_bytrial(
    info,
    *,
    replay_n_byexperience_feederonly_bytrial,
    swr_n_byexperience_feederonly_bytrial,
):
    return get_replay_proportions_byexperience_bytrial(
        replay_n_byexperience_feederonly_bytrial, swr_n_byexperience_feederonly_bytrial
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_feederonly_bytrial",
)
def cache_combined_replay_proportions_byexperience(
    infos,
    group_name,
    *,
    replay_n_byexperience_feederonly_bytrial,
    swr_n_byexperience_feederonly_bytrial,
):
    return get_replay_proportions_byexperience_bytrial(
        replay_n_byexperience_feederonly_bytrial, swr_n_byexperience_feederonly_bytrial
    )


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_feederonly_bytrial_pval",
)
def cache_replay_proportions_byexperience_feederonly_bytrial_pval(
    info,
    *,
    replay_n_byexperience_feederonly_bytrial,
    swr_n_byexperience_feederonly_bytrial,
):
    return get_replay_proportions_byexperience_bytrial_pval(
        replay_n_byexperience_feederonly_bytrial, swr_n_byexperience_feederonly_bytrial
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_feederonly_bytrial_pval",
)
def cache_combined_replay_proportions_byexperience_feederonly_bytrial_pval(
    infos,
    group_name,
    *,
    replay_n_byexperience_feederonly_bytrial,
    swr_n_byexperience_feederonly_bytrial,
):
    return get_replay_proportions_byexperience_bytrial_pval(
        replay_n_byexperience_feederonly_bytrial, swr_n_byexperience_feederonly_bytrial
    )


@task(infos=meta_session.all_infos, cache_saves="swrs_byphase_nofeeder")
def cache_swrs_byphase_nofeeder(info, *, task_times, position_byzone, swrs_byphase):
    swrs_nofeeders = {phase: [] for phase in meta.run_times}
    for phase in meta.run_times:
        starts = []
        stops = []
        for swr in swrs_byphase[phase]:
            for zone in [
                "u",
                "full_shortcut",
                "novel",
                "exploratory",
            ]:
                zone_time = position_byzone[zone].time
                if swr.starts not in starts:
                    if np.allclose(
                        swr.centers,
                        zone_time[nept.find_nearest_idx(zone_time, swr.centers)],
                    ):
                        starts.append(swr.start)
                        stops.append(swr.stop)
        if len(starts) > 0:
            swrs_nofeeders[phase] = nept.Epoch(starts, stops)
        else:
            swrs_nofeeders[phase] = nept.Epoch([], [])
    return swrs_nofeeders


@task(infos=meta_session.all_infos, cache_saves="swr_n_byexperience_nofeeder_bytrial")
def cache_swr_n_byexperience_nofeeder_bytrial(info, *, trials, swrs_byphase_nofeeder):
    return get_swrs_byexperience_bytrial(trials, swrs_byphase_nofeeder)


@task(groups=meta_session.groups, cache_saves="swr_n_byexperience_nofeeder_bytrial")
def cache_combined_swr_n_byexperience_nofeeder_bytrial(
    infos, group_name, *, all_swr_n_byexperience_nofeeder_bytrial
):
    return {
        experience: sum(
            swr_n_byexperience[experience]
            for swr_n_byexperience in all_swr_n_byexperience_nofeeder_bytrial
        )
        for experience in meta.experiences
    }


@task(infos=meta_session.all_infos, cache_saves="replays_byphase_nofeeder")
def cache_replays_byphase_nofeeder(info, *, position_byzone, replays_byphase):
    replays_nofeeders = {
        trajectory: {phase: [] for phase in meta.run_times}
        for trajectory in replays_byphase.keys()
    }
    for trajectory in replays_byphase.keys():
        for phase in meta.run_times:
            starts = []
            stops = []
            for replay in replays_byphase[trajectory][phase]:
                for zone in [
                    "u",
                    "full_shortcut",
                    "novel",
                    "exploratory",
                ]:
                    zone_time = position_byzone[zone].time
                    if zone_time.size > 0:
                        if replay.starts not in starts:
                            if np.allclose(
                                replay.centers,
                                zone_time[
                                    nept.find_nearest_idx(zone_time, replay.centers)
                                ],
                            ):
                                starts.append(replay.start)
                                stops.append(replay.stop)
            if len(starts) > 0:
                replays_nofeeders[trajectory][phase] = nept.Epoch(starts, stops)
            else:
                replays_nofeeders[trajectory][phase] = nept.Epoch([], [])
    return replays_nofeeders


@task(
    infos=meta_session.all_infos, cache_saves="replay_n_byexperience_nofeeder_bytrial"
)
def cache_replay_n_byexperience_nofeeder_bytrial(
    info, *, trials, replays_byphase_nofeeder
):
    return get_replays_byexperience_bytrial(trials, replays_byphase_nofeeder)


@task(groups=meta_session.groups, cache_saves="replay_n_byexperience_nofeeder_bytrial")
def cache_combined_replay_n_byexperience_nofeeder_bytrial(
    infos, group_name, *, all_replay_n_byexperience_nofeeder_bytrial
):
    return {
        trajectory: {
            experience: sum(
                replay_n_byexperience[trajectory][experience]
                for replay_n_byexperience in all_replay_n_byexperience_nofeeder_bytrial
            )
            for experience in meta.experiences
        }
        for trajectory in all_replay_n_byexperience_nofeeder_bytrial[0]
    }


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_nofeeder_bytrial",
)
def cache_replay_proportions_byexperience_nofeederonly(
    info, *, replay_n_byexperience_nofeeder_bytrial, swr_n_byexperience_nofeeder_bytrial
):
    return get_replay_proportions_byexperience_bytrial(
        replay_n_byexperience_nofeeder_bytrial, swr_n_byexperience_nofeeder_bytrial
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_nofeeder_bytrial",
)
def cache_combined_replay_proportions_byexperience_nofeeder_bytrial(
    infos,
    group_name,
    *,
    replay_n_byexperience_nofeeder_bytrial,
    swr_n_byexperience_nofeeder_bytrial,
):
    return get_replay_proportions_byexperience_bytrial(
        replay_n_byexperience_nofeeder_bytrial, swr_n_byexperience_nofeeder_bytrial
    )


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_nofeeder_bytrial_pval",
)
def cache_replay_proportions_byexperience_nofeeder_bytrial_pval(
    info, *, replay_n_byexperience_nofeeder_bytrial, swr_n_byexperience_nofeeder_bytrial
):
    return get_replay_proportions_byexperience_bytrial_pval(
        replay_n_byexperience_nofeeder_bytrial, swr_n_byexperience_nofeeder_bytrial
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_nofeeder_bytrial_pval",
)
def cache_combined_replay_proportions_byexperience_nofeeder_bytrial_pval(
    infos,
    group_name,
    *,
    replay_n_byexperience_nofeeder_bytrial,
    swr_n_byexperience_nofeeder_bytrial,
):
    return get_replay_proportions_byexperience_bytrial_pval(
        replay_n_byexperience_nofeeder_bytrial, swr_n_byexperience_nofeeder_bytrial
    )


@task(infos=meta_session.all_infos, cache_saves="swr_n_byexperience_feederonly")
def cache_swr_n_byexperience_feederonly(
    info, *, task_times, trials, swrs_byphase_feederonly
):
    return get_swrs_byexperience(task_times, trials, swrs_byphase_feederonly)


@task(groups=meta_session.groups, cache_saves="swr_n_byexperience_feederonly")
def cache_combined_swr_n_byexperience_feederonly(
    infos, group_name, *, all_swr_n_byexperience_feederonly
):
    return {
        experience: sum(
            swr_n_byexperience[experience]
            for swr_n_byexperience in all_swr_n_byexperience_feederonly
        )
        for experience in meta.on_task
    }


@task(infos=meta_session.all_infos, cache_saves="replay_n_byexperience_feederonly")
def cache_replay_n_byexperience_feederonly(
    info, *, task_times, trials, replays_byphase_feederonly
):
    return get_replays_byexperience(task_times, trials, replays_byphase_feederonly)


@task(groups=meta_session.groups, cache_saves="replay_n_byexperience_feederonly")
def cache_combined_replay_n_byexperience_feederonly(
    infos, group_name, *, all_replay_n_byexperience_feederonly
):
    return {
        trajectory: {
            experience: sum(
                replay_n_byexperience[trajectory][experience]
                for replay_n_byexperience in all_replay_n_byexperience_feederonly
            )
            for experience in meta.on_task
        }
        for trajectory in all_replay_n_byexperience_feederonly[0]
    }


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_feederonly",
)
def cache_replay_proportions_byexperience_feederonly(
    info,
    *,
    replay_n_byexperience_feederonly,
    swr_n_byexperience_feederonly,
):
    return get_replay_proportions_byexperience(
        replay_n_byexperience_feederonly, swr_n_byexperience_feederonly
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_feederonly",
)
def cache_combined_replay_proportions_byexperience_feederonly(
    infos,
    group_name,
    *,
    replay_n_byexperience_feederonly,
    swr_n_byexperience_feederonly,
):
    return get_replay_proportions_byexperience(
        replay_n_byexperience_feederonly, swr_n_byexperience_feederonly
    )


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_feederonly_pval",
)
def cache_replay_proportions_byexperience_feederonly_pval(
    info,
    *,
    replay_n_byexperience_feederonly,
    swr_n_byexperience_feederonly,
):
    return get_replay_proportions_byexperience_pval(
        replay_n_byexperience_feederonly, swr_n_byexperience_feederonly
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_feederonly_pval",
)
def cache_combined_replay_proportions_byexperience_feederonly_pval(
    infos,
    group_name,
    *,
    replay_n_byexperience_feederonly,
    swr_n_byexperience_feederonly,
):
    return get_replay_proportions_byexperience_pval(
        replay_n_byexperience_feederonly, swr_n_byexperience_feederonly
    )


@task(infos=meta_session.all_infos, cache_saves="swr_n_byexperience_nofeeder")
def cache_swr_n_byexperience_nofeeder(
    info, *, task_times, trials, swrs_byphase_nofeeder
):
    return get_swrs_byexperience(task_times, trials, swrs_byphase_nofeeder)


@task(groups=meta_session.groups, cache_saves="swr_n_byexperience_nofeeder")
def cache_combined_swr_n_byexperience_nofeeder(
    infos, group_name, *, all_swr_n_byexperience_nofeeder
):
    return {
        experience: sum(
            swr_n_byexperience[experience]
            for swr_n_byexperience in all_swr_n_byexperience_nofeeder
        )
        for experience in meta.on_task
    }


@task(infos=meta_session.all_infos, cache_saves="replay_n_byexperience_nofeeder")
def cache_replay_n_byexperience_nofeeder(
    info, *, task_times, trials, replays_byphase_nofeeder
):
    return get_replays_byexperience(task_times, trials, replays_byphase_nofeeder)


@task(groups=meta_session.groups, cache_saves="replay_n_byexperience_nofeeder")
def cache_combined_replay_n_byexperience_nofeeder(
    infos, group_name, *, all_replay_n_byexperience_nofeeder
):
    return {
        trajectory: {
            experience: sum(
                replay_n_byexperience[trajectory][experience]
                for replay_n_byexperience in all_replay_n_byexperience_nofeeder
            )
            for experience in meta.on_task
        }
        for trajectory in all_replay_n_byexperience_nofeeder[0]
    }


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_nofeeder",
)
def cache_replay_proportions_byexperience_nofeeder(
    info,
    *,
    replay_n_byexperience_nofeeder,
    swr_n_byexperience_nofeeder,
):
    return get_replay_proportions_byexperience(
        replay_n_byexperience_nofeeder, swr_n_byexperience_nofeeder
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_nofeeder",
)
def cache_combined_replay_proportions_byexperience_nofeeder(
    infos,
    group_name,
    *,
    replay_n_byexperience_nofeeder,
    swr_n_byexperience_nofeeder,
):
    return get_replay_proportions_byexperience(
        replay_n_byexperience_nofeeder, swr_n_byexperience_nofeeder
    )


@task(
    infos=meta_session.all_infos,
    cache_saves="replay_proportions_byexperience_nofeeder_pval",
)
def cache_replay_proportions_byexperience_nofeeder_pval(
    info,
    *,
    replay_n_byexperience_nofeeder,
    swr_n_byexperience_nofeeder,
):
    return get_replay_proportions_byexperience_pval(
        replay_n_byexperience_nofeeder, swr_n_byexperience_nofeeder
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_proportions_byexperience_nofeeder_pval",
)
def cache_combined_replay_proportions_byexperience_nofeeder_pval(
    infos,
    group_name,
    *,
    replay_n_byexperience_nofeeder,
    swr_n_byexperience_nofeeder,
):
    return get_replay_proportions_byexperience_pval(
        replay_n_byexperience_nofeeder, swr_n_byexperience_nofeeder
    )
