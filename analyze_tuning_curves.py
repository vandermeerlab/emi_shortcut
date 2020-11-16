import nept
import numpy as np
import scipy.interpolate
import scipy.stats
from shapely.geometry import Point

import meta
import meta_session
import paths
from tasks import task
from utils import latex_float


def has_field(tuning_curve):
    # If a neuron has a field near the end of the track, it might not be included
    # though it would be included if we did this check before clipping the end of
    # the field. Therefore, we add some a few valid bins to the end of diff to make
    # sure these are included. meta.consecutive_bins = 5, so we add 4 on either side

    diffs = np.diff(
        np.hstack(([0, 1, 1, 1, 1], tuning_curve > meta.min_hz, [1, 1, 1, 1, 0]))
    )
    field_lengths = np.where(diffs < 0)[0] - np.where(diffs > 0)
    return (
        np.any(field_lengths > meta.consecutive_bins)
        and np.nanmax(tuning_curve) > meta.peak_hz_above
    )


def restrict_linear_and_spikes(
    linear, spikes, maze_times, trials, *, speed_limit, t_smooth
):
    # restrict to maze times
    linear = linear[maze_times]
    spikes = [
        spiketrain.time_slice(maze_times.starts, maze_times.stops)
        for spiketrain in spikes
    ]

    # restrict to trials
    linear = linear[trials]
    spikes = [
        spiketrain.time_slice(trials.starts, trials.stops) for spiketrain in spikes
    ]

    # speed threshold
    run_epoch = nept.run_threshold(linear, thresh=speed_limit, t_smooth=t_smooth)
    linear = linear[run_epoch]
    spikes = [
        spiketrain.time_slice(run_epoch.starts, run_epoch.stops)
        for spiketrain in spikes
    ]
    return linear, spikes


def filter_and_sort(tuning_curves, spikes):
    order = [i for i in range(tuning_curves.shape[0])]

    # Remove inactive neurons
    order = [i for i in order if spikes[i].time.size > meta.min_n_spikes]

    # Remove neurons without fields
    order = [i for i in order if has_field(tuning_curves[i])]

    # Order by location of max peak
    maxpeak_loc = [np.argmax(tuning_curves[i]) for i in order]
    return [order[i] for i in np.argsort(maxpeak_loc)]


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_raw_tuning_spikes", "raw_linear_restricted"],
)
def cache_full_raw_tuning_spikes(info, *, task_times, raw_linear, spikes, trials):
    linear = {}
    tuning_spikes = {}
    for trajectory in meta.trajectories:
        linear[trajectory], tuning_spikes[trajectory] = restrict_linear_and_spikes(
            linear=raw_linear[f"{trajectory}_with_feeders"],
            spikes=spikes,
            maze_times=task_times["maze_times"],
            trials=trials[trajectory],
            speed_limit=meta.speed_limit,
            t_smooth=meta.t_smooth,
        )
    return {"full_raw_tuning_spikes": tuning_spikes, "raw_linear_restricted": linear}


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_raw_tuning_curves", "raw_occupancy"],
)
def cache_full_raw_tuning_curves(
    info, *, raw_linear_restricted, full_raw_tuning_spikes, lines
):
    tcs = {}
    occ = {}
    for trajectory in meta.trajectories:
        linear_max = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            + meta.feeder_dist
        )
        tcs[trajectory], occ[trajectory] = nept.tuning_curve_1d(
            raw_linear_restricted[trajectory],
            full_raw_tuning_spikes[trajectory],
            edges=nept.get_edges(
                0,
                linear_max,
                binsize=meta.tc_binsize,
                lastbin=False,
            ),
            gaussian_std=meta.gaussian_std,
            min_occupancy=meta.min_occupancy,
        )
    return {"full_raw_tuning_curves": tcs, "raw_occupancy": occ}


@task(infos=meta_session.all_infos, cache_saves="raw_tc_order")
def cache_raw_tc_order(info, *, full_raw_tuning_curves, full_raw_tuning_spikes):
    return {
        trajectory: filter_and_sort(
            tuning_curves=full_raw_tuning_curves[trajectory],
            spikes=full_raw_tuning_spikes[trajectory],
        )
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="raw_tuning_curves")
def cache_raw_tuning_curves(info, *, full_raw_tuning_curves, raw_tc_order):
    return {
        trajectory: full_raw_tuning_curves[trajectory][raw_tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="raw_tuning_spikes")
def cache_raw_tuning_spikes(info, *, full_raw_tuning_spikes, raw_tc_order):
    return {
        trajectory: [
            full_raw_tuning_spikes[trajectory][i] for i in raw_tc_order[trajectory]
        ]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="raw_tc_spikes")
def cache_raw_tc_spikes(info, *, spikes, raw_tc_order):
    return {
        trajectory: [spikes[i] for i in raw_tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="raw_test_tuning_spikes")
def cache_raw_test_tuning_spikes(info, *, task_times, raw_linear, spikes, trials):
    tuning_spikes = {}
    for trajectory in meta.trajectories:
        # Generate a single 3 Hz tuning curve
        _, tuning_spikes[trajectory] = restrict_linear_and_spikes(
            linear=raw_linear[f"{trajectory}_with_feeders"],
            spikes=[
                nept.SpikeTrain(
                    time=np.arange(
                        raw_linear[trajectory].time[0] + jitter,
                        raw_linear[trajectory].time[-1] + jitter,
                        step=1 / 3,
                    ),
                )
                for jitter in np.linspace(0, 1 / 3, 200)
            ],
            maze_times=task_times["maze_times"],
            trials=trials[trajectory],
            speed_limit=meta.speed_limit,
            t_smooth=meta.t_smooth,
        )
    return tuning_spikes


@task(infos=meta_session.all_infos, cache_saves="raw_test_tuning_curves")
def cache_raw_test_tuning_curves(
    info, *, raw_linear_restricted, raw_test_tuning_spikes, lines
):
    tcs = {}
    for trajectory in meta.trajectories:
        linear_max = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            + meta.feeder_dist
        )
        tcs[trajectory], _ = nept.tuning_curve_1d(
            raw_linear_restricted[trajectory],
            raw_test_tuning_spikes[trajectory],
            edges=nept.get_edges(
                0,
                linear_max,
                binsize=meta.tc_binsize,
                lastbin=False,
            ),
            gaussian_std=meta.gaussian_std,
            min_occupancy=meta.min_occupancy,
        )
    return tcs


@task(infos=meta_session.all_infos, cache_saves="test_tuning_spikes")
def cache_test_tuning_spikes(info, *, task_times, tc_linear, spikes, trials):
    tuning_spikes = {}
    for trajectory in meta.trajectories:
        # Generate a single 3 Hz tuning curve
        _, tuning_spikes[trajectory] = restrict_linear_and_spikes(
            linear=tc_linear[trajectory],
            spikes=[
                nept.SpikeTrain(
                    time=np.arange(
                        tc_linear[trajectory].time[0] + jitter,
                        tc_linear[trajectory].time[-1] + jitter,
                        step=1 / 3,
                    ),
                )
                for jitter in np.linspace(0, 1 / 3, 200)
            ],
            maze_times=task_times["maze_times"],
            trials=trials[trajectory],
            speed_limit=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )
    return tuning_spikes


@task(infos=meta_session.all_infos, cache_saves="test_tuning_curves")
def cache_test_tuning_curves(info, *, tc_linear_restricted, test_tuning_spikes, lines):
    tcs = {}
    for trajectory in meta.trajectories:
        tcs[trajectory], _ = nept.tuning_curve_1d(
            tc_linear_restricted[trajectory],
            test_tuning_spikes[trajectory],
            edges=meta.tc_linear_bin_edges,
            gaussian_std=meta.std_gaussian_std,
            min_occupancy=meta.std_min_occupancy,
        )
        tcs[trajectory] = tcs[trajectory][
            :, meta.tc_extra_bins_before : -meta.tc_extra_bins_after
        ]
        if not info.full_standard_maze:
            tcs[trajectory][
                :, meta.linear_bin_centers < meta.short_standard_points["feeder1"]
            ] = np.nan
    return tcs


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_tuning_spikes", "tc_linear_restricted"],
)
def cache_full_tuning_spikes(info, *, task_times, tc_linear, spikes, trials):
    linear = {}
    tuning_spikes = {}
    for trajectory in meta.trajectories:
        linear[trajectory], tuning_spikes[trajectory] = restrict_linear_and_spikes(
            linear=tc_linear[trajectory],
            spikes=spikes,
            maze_times=task_times["maze_times"],
            trials=trials[trajectory],
            speed_limit=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )
    return {"full_tuning_spikes": tuning_spikes, "tc_linear_restricted": linear}


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_tuning_curves", "occupancy"],
)
def cache_full_tuning_curves(info, *, tc_linear_restricted, full_tuning_spikes):
    tcs = {}
    occ = {}
    for trajectory in meta.trajectories:
        tcs[trajectory], occ[trajectory] = nept.tuning_curve_1d(
            tc_linear_restricted[trajectory],
            full_tuning_spikes[trajectory],
            edges=meta.tc_linear_bin_edges,
            gaussian_std=meta.std_gaussian_std,
            min_occupancy=meta.std_min_occupancy,
        )
        tcs[trajectory] = tcs[trajectory][
            :, meta.tc_extra_bins_before : -meta.tc_extra_bins_after
        ]
        if not info.full_standard_maze:
            tcs[trajectory][
                :, meta.linear_bin_centers < meta.short_standard_points["feeder1"]
            ] = np.nan
    return {"full_tuning_curves": tcs, "occupancy": occ}


@task(infos=meta_session.all_infos, cache_saves="tc_order")
def cache_tc_order(info, *, full_tuning_curves, full_tuning_spikes):
    return {
        trajectory: filter_and_sort(
            tuning_curves=full_tuning_curves[trajectory],
            spikes=full_tuning_spikes[trajectory],
        )
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="tuning_curves")
def cache_tuning_curves(info, *, full_tuning_curves, tc_order):
    return {
        trajectory: full_tuning_curves[trajectory][tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="tuning_spikes")
def cache_tuning_spikes(info, *, full_tuning_spikes, tc_order):
    return {
        trajectory: [full_tuning_spikes[trajectory][i] for i in tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="tc_spikes")
def cache_tc_spikes(info, *, spikes, tc_order):
    return {
        trajectory: [spikes[i] for i in tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_matched_tuning_spikes", "tc_matched_linear_restricted"],
)
def cache_full_matched_tuning_spikes(
    info, *, task_times, lines, tc_matched_linear, spikes, trials
):
    linear = {}
    tuning_spikes = {}
    for trajectory in meta.trajectories:
        linear[trajectory], tuning_spikes[trajectory] = restrict_linear_and_spikes(
            linear=tc_matched_linear[trajectory],
            spikes=spikes,
            maze_times=task_times["maze_times"],
            trials=trials[trajectory],
            speed_limit=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )
    return {
        "full_matched_tuning_spikes": tuning_spikes,
        "tc_matched_linear_restricted": linear,
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_matched_tuning_curves", "matched_occupancy"],
)
def cache_full_matched_tuning_curves(
    info, *, tc_matched_linear_restricted, full_matched_tuning_spikes
):
    tcs = {}
    occ = {}
    for trajectory in meta.trajectories:
        tcs[trajectory], occ[trajectory] = nept.tuning_curve_1d(
            tc_matched_linear_restricted[trajectory],
            full_matched_tuning_spikes[trajectory],
            edges=meta.tc_linear_bin_edges,
            gaussian_std=meta.std_gaussian_std,
            min_occupancy=meta.std_min_occupancy,
        )
        tcs[trajectory] = tcs[trajectory][
            :, meta.tc_extra_bins_before : -meta.tc_extra_bins_after
        ]
    return {"full_matched_tuning_curves": tcs, "matched_occupancy": occ}


@task(infos=meta_session.all_infos, cache_saves="matched_tc_order")
def cache_matched_tc_order(
    info, *, full_matched_tuning_curves, full_matched_tuning_spikes
):
    return {
        trajectory: filter_and_sort(
            tuning_curves=full_matched_tuning_curves[trajectory],
            spikes=full_matched_tuning_spikes[trajectory],
        )
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="matched_tuning_curves")
def cache_matched_tuning_curves(info, *, full_matched_tuning_curves, matched_tc_order):
    return {
        trajectory: full_matched_tuning_curves[trajectory][matched_tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="matched_tuning_spikes")
def cache_matched_tuning_spikes(info, *, full_matched_tuning_spikes, matched_tc_order):
    return {
        trajectory: [
            full_matched_tuning_spikes[trajectory][i]
            for i in matched_tc_order[trajectory]
        ]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="matched_tc_spikes")
def cache_matched_tc_spikes(info, *, spikes, matched_tc_order):
    return {
        trajectory: [spikes[i] for i in matched_tc_order[trajectory]]
        for trajectory in meta.trajectories
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=["full_joined_tuning_spikes", "joined_linear_restricted"],
)
def cache_full_joined_tuning_spikes(info, *, task_times, joined_linear, spikes, trials):
    linear, tuning_spikes = restrict_linear_and_spikes(
        linear=joined_linear,
        spikes=spikes,
        maze_times=task_times["maze_times"],
        trials=trials["u"].join(trials["full_shortcut"]),
        speed_limit=meta.std_speed_limit * 0.5,
        t_smooth=meta.std_t_smooth,
    )
    return {
        "full_joined_tuning_spikes": tuning_spikes,
        "joined_linear_restricted": linear,
    }


@task(infos=meta_session.all_infos, cache_saves="full_joined_tuning_curves")
def cache_full_joined_tuning_curves(info, *, full_matched_tuning_curves):
    n_tcs = full_matched_tuning_curves["u"].shape[0]
    assert full_matched_tuning_curves["full_shortcut"].shape[0] == n_tcs
    tcs = np.zeros((n_tcs, 100))
    tcs[:, :50] = scipy.signal.decimate(full_matched_tuning_curves["u"], 2)
    tcs[:, 50:] = scipy.signal.decimate(full_matched_tuning_curves["full_shortcut"], 2)
    return tcs


@task(infos=meta_session.all_infos, cache_saves="joined_occupancy")
def cache_joined_occupancy(info, *, matched_occupancy):
    occ = np.zeros((100,))
    nofeeders = slice(meta.tc_extra_bins_before, -meta.tc_extra_bins_after)
    occ[:50] = scipy.signal.decimate(matched_occupancy["u"][nofeeders], 2)
    occ[50:] = scipy.signal.decimate(matched_occupancy["full_shortcut"][nofeeders], 2)
    return occ


@task(infos=meta_session.all_infos, cache_saves="joined_tc_order")
def cache_joined_tc_order(
    info, *, full_joined_tuning_curves, full_joined_tuning_spikes
):
    return filter_and_sort(
        tuning_curves=full_joined_tuning_curves, spikes=full_joined_tuning_spikes
    )


@task(infos=meta_session.all_infos, cache_saves="joined_tuning_curves")
def cache_joined_tuning_curves(info, *, full_joined_tuning_curves, joined_tc_order):
    return full_joined_tuning_curves[joined_tc_order]


@task(infos=meta_session.all_infos, cache_saves="joined_tuning_spikes")
def cache_joined_tuning_spikes(info, *, full_joined_tuning_spikes, joined_tc_order):
    return [full_joined_tuning_spikes[i] for i in joined_tc_order]


@task(infos=meta_session.all_infos, cache_saves="joined_tc_spikes")
def cache_joined_tc_spikes(info, *, spikes, joined_tc_order):
    return [spikes[i] for i in joined_tc_order]


@task(infos=meta_session.all_infos, cache_saves="tuning_spikes_position")
def cache_tuning_spikes_position(info, *, position, tuning_spikes):
    tc_spikes_position = {}
    for trajectory in meta.trajectories:
        tc_spikes_position[trajectory] = []
        for spiketrain in tuning_spikes[trajectory]:
            f_xy = scipy.interpolate.interp1d(
                position.time, position.data.T, kind="nearest", fill_value="extrapolate"
            )
            tc_spikes_position[trajectory].append(
                nept.Position(f_xy(spiketrain.time), spiketrain.time)
            )
    return tc_spikes_position


@task(infos=meta_session.all_infos, cache_saves="tuning_spikes_histogram")
def cache_tuning_spikes_histogram(info, *, tuning_spikes_position):
    return {
        trajectory: [
            np.histogram2d(pos.y, pos.x, bins=[info.yedges, info.xedges])[0]
            for pos in tuning_spikes_position[trajectory]
        ]
        for trajectory in meta.trajectories
    }


@task(
    groups=meta_session.analysis_grouped, savepath=("data", "n_neurons_with_fields.tex")
)
def save_n_neurons_with_fields(
    infos, group_name, *, all_tuning_curves, all_spikes, savepath
):
    total_n = {trajectory: 0 for trajectory in meta.trajectories}
    total_withfields = 0
    total_neurons = 0
    with open(savepath, "w") as fp:
        for info, tuning_curves, spikes in zip(infos, all_tuning_curves, all_spikes):
            total_neurons += len(spikes)
            print(f"% {info.session_id}", file=fp)
            for trajectory in meta.trajectories:
                total_n[trajectory] += len(tuning_curves[trajectory])
                total_withfields += len(tuning_curves[trajectory])
                print(
                    f"% Neurons with field(s) along {trajectory}: "
                    f"{len(tuning_curves[trajectory])}",
                    file=fp,
                )
            print("% ---------", file=fp)
        print("% Combined", file=fp)
        for trajectory in meta.trajectories:
            traj = trajectory.replace("_", "")
            print(
                fr"\def \n{traj}withfields/{{{total_n[trajectory]}}}",
                file=fp,
            )
            print(
                fr"\def \proportion{traj}withfields/{{{total_n[trajectory]/total_neurons * 100:.1f}}}",
                file=fp,
            )
        print(
            fr"\def \ntotalneurons/{{{total_neurons}}}",
            file=fp,
        )
        print(
            fr"\def \ntotalwithfields/{{{total_withfields}}}",
            file=fp,
        )
        print(
            fr"\def \proportiontotalwithfields/{{{total_withfields/total_neurons * 100:.1f}}}",
            file=fp,
        )


@task(
    groups=meta_session.all_grouped,
    savepath=("data", "n_neurons.table"),
)
def save_n_neurons(infos, group_name, *, all_spikes, savepath):
    with open(savepath, "w") as fp:
        print(
            r"""
\begin{tabular}{c c c c c c c c c}
\toprule
\textbf{Rat~ID} & \textbf{Day~1} & \textbf{Day~2} & \textbf{Day~3} & \textbf{Day~4} &
\textbf{Day~5} & \textbf{Day~6} & \textbf{Day~7} & \textbf{Day~8} \\ [0.5ex]
\midrule
        """.strip(),
            file=fp,
        )

        day_totals = [[0, 0] for _ in range(8)]
        for rat in ["63", "66", "67", "68"]:
            days = [None for _ in range(8)]
            for info, spikes in zip(infos, all_spikes):
                if rat not in info.rat_id:
                    continue

                spikepath = paths.recording_dir(info)
                spikes4 = nept.load_spikes(spikepath, load_questionable=False)
                spikes5 = nept.load_spikes(spikepath, load_questionable=True)

                day = int(info.session_id[-1]) - 1
                days[day] = (len(spikes5), len(spikes4))
                day_totals[day][0] += len(spikes5)
                day_totals[day][1] += len(spikes4)

            days = ["-" if day is None else rf"{day[0]}" for day in days]

            space = " [1ex]" if rat == "68" else ""
            print(
                rf"\textbf{{R0{rat}}} & {' & '.join(days)} \\{space}",
                file=fp,
            )

        day_totals = [rf"{day[0]}" for day in day_totals]
        print(r"\bottomrule", file=fp)
        print(
            rf"\textbf{{Total}} & {' & '.join(day_totals)} \\ [1ex]",
            file=fp,
        )
        print(r"\bottomrule", file=fp)
        print(r"\end{tabular}", file=fp)


@task(infos=meta_session.all_infos, cache_saves="raw_tc_mean")
def cache_raw_tc_mean(info, *, raw_tuning_curves):
    return {
        trajectory: np.nanmean(
            np.vstack(
                raw_tuning_curves[trajectory]
                if raw_tuning_curves[trajectory].shape[0] > 0
                else np.ones(100) * np.nan
            ),
            axis=0,
        )
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="raw_test_tc_mean")
def cache_raw_test_tc_mean(info, *, raw_test_tuning_curves):
    return {
        trajectory: np.nanmean(
            np.vstack(
                raw_test_tuning_curves[trajectory]
                if raw_test_tuning_curves[trajectory].shape[0] > 0
                else np.ones(100) * np.nan
            ),
            axis=0,
        )
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="test_tc_mean")
def cache_test_tc_mean(info, *, test_tuning_curves):
    return {
        trajectory: np.nanmean(np.vstack(test_tuning_curves[trajectory]), axis=0)
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="tc_mean")
def cache_tc_mean(info, *, tuning_curves):
    return {
        trajectory: np.nanmean(np.vstack(tuning_curves[trajectory]), axis=0)
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="matched_tc_mean")
def cache_matched_tc_mean(info, *, matched_tuning_curves):
    return {
        trajectory: np.nanmean(np.vstack(matched_tuning_curves[trajectory]), axis=0)
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="joined_tc_mean")
def cache_joined_tc_mean(info, *, joined_tuning_curves):
    return np.nanmean(np.vstack(joined_tuning_curves), axis=0)


@task(infos=meta_session.all_infos, cache_saves="tc_mean_normalized")
def cache_tc_mean_normalized(info, *, tuning_curves):
    return {
        trajectory: np.nanmean(
            np.vstack([tc / np.nansum(tc) for tc in tuning_curves[trajectory]]),
            axis=0,
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="tc_mean")
def cache_combined_tc_mean(infos, group_name, *, all_tc_mean):
    return {
        trajectory: np.nanmean(
            np.vstack([tc_mean[trajectory] for tc_mean in all_tc_mean]), axis=0
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="matched_tc_mean")
def cache_combined_matched_tc_mean(infos, group_name, *, all_matched_tc_mean):
    return {
        trajectory: np.nanmean(
            np.vstack([tc_mean[trajectory] for tc_mean in all_matched_tc_mean]), axis=0
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="joined_tc_mean")
def cache_combined_joined_tc_mean(infos, group_name, *, all_joined_tc_mean):
    return np.nanmean(np.vstack([tc_mean for tc_mean in all_joined_tc_mean]), axis=0)


@task(groups=meta_session.groups, cache_saves="tc_mean_normalized")
def cache_combined_tc_mean_normalized(infos, group_name, *, all_tc_mean_normalized):
    return {
        trajectory: np.nanmean(
            [tc_mean[trajectory] for tc_mean in all_tc_mean_normalized],
            axis=0,
        )
        for trajectory in meta.trajectories
    }


@task(
    infos=meta_session.all_infos,
    cache_saves=["u_tcs_byphase", "u_tcs_with_fields_byphase"],
)
def cache_u_tcs_byphase(info, *, tc_linear, task_times, trials, spikes):
    rng = np.random.RandomState(seed=meta.seed)
    u_tcs_byphase = {}
    min_n_trials = min(
        trials["u"].time_slice(task_times[phase].start, task_times[phase].stop).n_epochs
        for phase in meta.run_times
    )
    with_fields = {}

    for phase in meta.run_times:
        phase_trials = trials["u"].time_slice(
            task_times[phase].start, task_times[phase].stop
        )
        # Only use a random min_n_trials trials in that phase
        phase_trials = phase_trials[
            rng.choice(
                np.arange(phase_trials.n_epochs, dtype=int),
                size=min_n_trials,
                replace=False,
            )
        ]
        assert phase_trials.n_epochs == min_n_trials

        phase_linear, phase_tuning_spikes = restrict_linear_and_spikes(
            linear=tc_linear["u"],
            spikes=spikes,
            maze_times=task_times[phase],
            trials=phase_trials,
            speed_limit=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )

        # get tuning curve
        tuning_curves, _ = nept.tuning_curve_1d(
            phase_linear,
            phase_tuning_spikes,
            meta.tc_linear_bin_edges,
            gaussian_std=meta.std_gaussian_std,
            min_occupancy=meta.std_min_occupancy,
        )
        tuning_curves = tuning_curves[
            :, meta.tc_extra_bins_before : -meta.tc_extra_bins_after
        ]
        if not info.full_standard_maze:
            tuning_curves[
                :, meta.linear_bin_centers < meta.short_standard_points["feeder1"]
            ] = np.nan

        u_tcs_byphase[phase] = tuning_curves
        with_fields[phase] = np.array(
            [has_field(tc) for tc in u_tcs_byphase[phase]], dtype=bool
        )

    with_field_anyphase = np.array(
        [
            any(with_fields[phase][i] for phase in meta.run_times)
            for i in range(tuning_curves.shape[0])
        ],
        dtype=bool,
    )
    u_tcs_byphase = {
        phase: u_tcs[with_field_anyphase] for phase, u_tcs in u_tcs_byphase.items()
    }
    with_fields = {
        phase: with_fields[phase][with_field_anyphase] for phase in meta.run_times
    }
    return {"u_tcs_byphase": u_tcs_byphase, "u_tcs_with_fields_byphase": with_fields}


@task(infos=meta_session.analysis_infos, cache_saves="u_tcs_byphase_mean")
def cache_u_tcs_byphase_mean(info, *, u_tcs_byphase):
    return {phase: np.nanmean(u_tcs_byphase[phase], axis=0) for phase in meta.run_times}


@task(infos=meta_session.analysis_infos, cache_saves="u_tcs_byphase_mean_normalized")
def cache_u_tcs_byphase_mean_normalized(info, *, u_tcs_byphase):
    return {
        phase: np.nanmean(
            np.vstack([tc / np.nansum(tc) for tc in u_tcs_byphase[phase]]), axis=0
        )
        for phase in meta.run_times
    }


@task(groups=meta_session.groups, cache_saves="u_tcs_byphase_mean")
def cache_combined_u_tcs_byphase_mean(infos, group_name, *, all_u_tcs_byphase):
    return {
        phase: np.nanmean(
            np.vstack([u_tcs_byphase[phase] for u_tcs_byphase in all_u_tcs_byphase]),
            axis=0,
        )
        for phase in meta.run_times
    }


@task(groups=meta_session.groups, cache_saves="u_tcs_byphase_mean_normalized")
def cache_combined_u_tcs_byphase_mean_normalized(
    infos, group_name, *, all_u_tcs_byphase
):
    return {
        phase: np.nanmean(
            np.vstack(
                [
                    np.vstack([tc / np.nansum(tc) for tc in u_tcs_byphase[phase]])
                    for u_tcs_byphase in all_u_tcs_byphase
                ]
            ),
            axis=0,
        )
        for phase in meta.run_times
    }


@task(infos=meta_session.all_infos, cache_saves="tc_correlations")
def cache_tc_correlations(info, *, u_tcs_byphase):
    tc_correlations = {phases: [] for phases in meta.phases_corr}

    for left, right in [("1", "2"), ("1", "3"), ("2", "3")]:
        for neuron_left, neuron_right in zip(
            u_tcs_byphase[f"phase{left}"], u_tcs_byphase[f"phase{right}"]
        ):
            valid = (~np.isnan(neuron_left)) & (~np.isnan(neuron_right))
            neuron_left = neuron_left[valid]
            neuron_right = neuron_right[valid]
            correlation, _ = scipy.stats.pearsonr(neuron_left, neuron_right)
            tc_correlations[f"phases{left}{right}"].append(
                0 if np.isnan(correlation) else correlation
            )

    return {phases: np.array(tc_correlations[phases]) for phases in meta.phases_corr}


@task(groups=meta_session.groups, cache_saves="tc_correlations")
def cache_combined_tc_correlations(infos, group_name, *, all_tc_correlations):
    return {
        phases: np.hstack(
            [tc_correlations[phases] for tc_correlations in all_tc_correlations]
        )
        for phases in meta.phases_corr
    }


@task(groups=meta_session.analysis_grouped, savepath=("tcs", "tc_correlations.tex"))
def save_tc_correlations(infos, group_name, *, tc_correlations, savepath):
    with open(savepath, "w") as fp:
        print("% TC correlation stats", file=fp)
        mean12 = np.mean(tc_correlations["phases12"])
        sem12 = scipy.stats.sem(tc_correlations["phases12"])
        mean23 = np.mean(tc_correlations["phases23"])
        sem23 = scipy.stats.sem(tc_correlations["phases23"])
        print(fr"\def \tcbtwonetwomean/{{{mean12:.2f}}}", file=fp)
        print(fr"\def \tcbtwonetwosem/{{{sem12:.2f}}}", file=fp)
        print(fr"\def \tcbtwtwothreemean/{{{mean23:.2f}}}", file=fp)
        print(fr"\def \tcbtwtwothreesem/{{{sem23:.2f}}}", file=fp)
        stats, pval = scipy.stats.mannwhitneyu(
            tc_correlations["phases12"], tc_correlations["phases23"]
        )
        pval = latex_float(pval)
        print(fr"\def \tccorr/{{{stats}}}", file=fp)
        print(fr"\def \tccorrpval/{{{pval}}}", file=fp)


@task(infos=meta_session.all_infos, cache_saves="tc_correlations_bybin")
def cache_tc_correlations_bybin(info, *, u_tcs_byphase):
    tc_correlations_bybin = {phases: [] for phases in meta.phases_corr}
    n_bins = u_tcs_byphase["phase1"].shape[1]

    for left, right in [("1", "2"), ("1", "3"), ("2", "3")]:
        for i in range(n_bins):
            left_bin = u_tcs_byphase[f"phase{left}"][:, i]
            right_bin = u_tcs_byphase[f"phase{right}"][:, i]
            valid = (~np.isnan(left_bin)) & (~np.isnan(right_bin))
            if np.sum(valid) < 2:
                correlation = 0
            else:
                correlation, _ = scipy.stats.pearsonr(left_bin[valid], right_bin[valid])
            tc_correlations_bybin[f"phases{left}{right}"].append(correlation)

    return {
        phases: np.array(tc_correlations_bybin[phases]) for phases in meta.phases_corr
    }


@task(groups=meta_session.groups, cache_saves="tc_correlations_bybin")
def cache_combined_tc_correlations_bybin(infos, group_name, *, all_u_tcs_byphase):
    tc_correlations_bybin = {phases: [] for phases in meta.phases_corr}
    n_bins = all_u_tcs_byphase[0]["phase1"].shape[1]

    for left, right in [("1", "2"), ("1", "3"), ("2", "3")]:
        left_tcs = np.vstack(
            tcs_byphase[f"phase{left}"] for tcs_byphase in all_u_tcs_byphase
        )
        right_tcs = np.vstack(
            tcs_byphase[f"phase{right}"] for tcs_byphase in all_u_tcs_byphase
        )
        for i in range(n_bins):
            valid = (~np.isnan(left_tcs[:, i])) & (~np.isnan(right_tcs[:, i]))
            if np.sum(valid) < 2:
                correlation = 0
            else:
                correlation, _ = scipy.stats.pearsonr(
                    left_tcs[:, i][valid], right_tcs[:, i][valid]
                )

            tc_correlations_bybin[f"phases{left}{right}"].append(correlation)

    return {
        phases: np.array(tc_correlations_bybin[phases]) for phases in meta.phases_corr
    }


@task(
    groups=meta_session.analysis_grouped, savepath=("tcs", "tc_correlations_bybin.tex")
)
def save_tc_correlations_bybin(infos, group_name, *, tc_correlations_bybin, savepath):
    dist_to_landmark = np.tile(np.hstack([np.arange(10), np.arange(9, -1, -1)]), 5)
    left = np.hstack([np.arange(20, -1, -1), np.arange(1, 31)])
    dist_to_shortcut = np.hstack([left, left[-2:0:-1]])

    with open(savepath, "w") as fp:
        for ph, text in zip(["12", "23"], ["onetwo", "twothree"]):
            nan_idx = np.isnan(tc_correlations_bybin[f"phases{ph}"])

            corr, pval = scipy.stats.pearsonr(
                tc_correlations_bybin[f"phases{ph}"][~nan_idx],
                dist_to_landmark[~nan_idx],
            )
            print(fr"\def \phase{text}bybinlandmarkcorr/{{{corr:.2f}}}", file=fp)
            print(fr"\def \phase{text}bybinlandmarkpval/{{{pval:.3g}}}", file=fp)
            corr, pval = scipy.stats.pearsonr(
                tc_correlations_bybin[f"phases{ph}"][~nan_idx],
                dist_to_shortcut[~nan_idx],
            )
            print(fr"\def \phase{text}bybinshortcutcorr/{{{corr:.2f}}}", file=fp)
            print(fr"\def \phase{text}bybinshortcutpval/{{{pval:.3g}}}", file=fp)


@task(infos=meta_session.all_infos, cache_saves="tc_fields_appear")
def cache_tc_fields_appear(info, *, u_tcs_with_fields_byphase):
    appear = {}
    for left, right in [("1", "2"), ("1", "3"), ("2", "3")]:
        appear[f"phases{left}{right}"] = (
            ~u_tcs_with_fields_byphase[f"phase{left}"]
            & u_tcs_with_fields_byphase[f"phase{right}"]
        )
    return appear


@task(groups=meta_session.groups, cache_saves="tc_fields_appear")
def cache_combined_tc_fields_appear(infos, group_name, *, all_tc_fields_appear):
    return {
        phases: np.hstack(appear[phases] for appear in all_tc_fields_appear)
        for phases in meta.phases_corr
    }


@task(infos=meta_session.all_infos, cache_saves="tc_fields_disappear")
def cache_tc_fields_disappear(info, *, u_tcs_with_fields_byphase):
    disappear = {}
    for left, right in [("1", "2"), ("1", "3"), ("2", "3")]:
        disappear[f"phases{left}{right}"] = (
            u_tcs_with_fields_byphase[f"phase{left}"]
            & ~u_tcs_with_fields_byphase[f"phase{right}"]
        )
    return disappear


@task(groups=meta_session.groups, cache_saves="tc_fields_disappear")
def cache_combined_tc_fields_disappear(infos, group_name, *, all_tc_fields_disappear):
    return {
        phases: np.hstack(disappear[phases] for disappear in all_tc_fields_disappear)
        for phases in meta.phases_corr
    }


@task(
    groups=meta_session.analysis_grouped,
    savepath=("tcs", "tc_n_remapping.tex"),
)
def save_n_remapping(
    infos,
    group_name,
    *,
    tc_fields_appear,
    tc_fields_disappear,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% Number of remapping neurons", file=fp)
        n_appear = {
            phases: np.sum(tc_fields_appear[phases]) for phases in meta.phases_corr
        }
        n_disappear = {
            phases: np.sum(tc_fields_disappear[phases]) for phases in meta.phases_corr
        }
        n_appear2 = n_appear["phases12"]
        n_appear3 = n_appear["phases23"]
        n_disappear2 = n_disappear["phases12"]
        n_disappear3 = n_disappear["phases23"]
        n_total2 = n_appear2 + n_disappear2
        n_total3 = n_appear3 + n_disappear3
        print(
            fr"\def \nappeartwo/{{{n_appear2}}}",
            file=fp,
        )
        print(
            fr"\def \nappearthree/{{{n_appear3}}}",
            file=fp,
        )
        print(
            fr"\def \ndisappeartwo/{{{n_disappear2}}}",
            file=fp,
        )
        print(
            fr"\def \ndisappearthree/{{{n_disappear3}}}",
            file=fp,
        )
        print(
            fr"\def \nremappingtwo/{{{n_total2}}}",
            file=fp,
        )
        print(
            fr"\def \nremappingthree/{{{n_total3}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(infos=meta_session.all_infos, cache_saves="tc_appear_mean")
def cache_tc_appear_mean(info, *, tc_fields_appear, u_tcs_byphase):
    return {
        phases: np.nanmean(
            u_tcs_byphase[f"phase{phases[-1]}"][tc_fields_appear[phases]], axis=0
        )
        for phases in meta.phases_corr
    }


@task(infos=meta_session.all_infos, cache_saves="tc_appear_maxpeaks")
def cache_tc_appear_maxpeaks(info, *, tc_fields_appear, u_tcs_byphase):
    return {
        phases: np.histogram(
            np.nanargmax(
                u_tcs_byphase[f"phase{phases[-1]}"][tc_fields_appear[phases]], axis=1
            ),
            bins=meta.linear_bin_edges,
        )[0]
        if np.sum(tc_fields_appear[phases]) > 0
        else np.zeros(100)
        for phases in meta.phases_corr
    }


@task(groups=meta_session.analysis_grouped, cache_saves="tc_appear_maxpeaks")
def cache_combined_tc_appear_maxpeaks(infos, group_name, *, all_tc_appear_maxpeaks):
    return {
        phases: np.sum(maxpeaks[phases] for maxpeaks in all_tc_appear_maxpeaks)
        for phases in meta.phases_corr
    }


@task(groups=meta_session.groups, cache_saves="tc_appear_correlations")
def cache_combined_tc_appear_correlations(
    infos, group_name, *, all_tc_fields_appear, all_u_tcs_byphase
):
    correlations = {
        phases: np.zeros((meta.linear_bin_centers.size, meta.linear_bin_centers.size))
        for phases in meta.phases_corr
    }

    for phases in meta.phases_corr:
        tcs_byphase = np.vstack(
            tcs[f"phase{phases[-1]}"][appear[phases]]
            for tcs, appear in zip(all_u_tcs_byphase, all_tc_fields_appear)
        )
        for i in range(meta.linear_bin_centers.size):
            for j in range(meta.linear_bin_centers.size):
                short = ["short_standard", "day2", "day3", "day4"]
                if group_name in short and (i < 20 or j < 20):
                    correlations[phases][i, j] = np.nan
                else:
                    left = tcs_byphase[:, i]
                    right = tcs_byphase[:, j]
                    valid = (~np.isnan(left)) & (~np.isnan(right))
                    if np.sum(valid) >= 2:
                        corr, _ = scipy.stats.pearsonr(left[valid], right[valid])
                        correlations[phases][i, j] = 0 if np.isnan(corr) else corr

    return correlations


@task(infos=meta_session.all_infos, cache_saves="tc_appear_mean_normalized")
def cache_tc_appear_mean_normalized(info, *, tc_fields_appear, u_tcs_byphase):
    return {
        phases: np.nanmean(
            np.vstack(
                [
                    tc / np.nansum(tc)
                    for tc in u_tcs_byphase[f"phase{phases[-1]}"][
                        tc_fields_appear[phases]
                    ]
                ]
            )
            if np.sum(tc_fields_appear[phases]) > 0
            else [],
            axis=0,
        )
        for phases in meta.phases_corr
    }


@task(groups=meta_session.groups, cache_saves="tc_appear_mean")
def cache_combined_tc_appear_mean(
    infos, group_name, *, all_tc_fields_appear, all_u_tcs_byphase
):
    tcs = {phases: [] for phases in meta.phases_corr}
    for u_tcs_byphase, appear in zip(all_u_tcs_byphase, all_tc_fields_appear):
        for phases in meta.phases_corr:
            tcs[phases].append(u_tcs_byphase[f"phase{phases[-1]}"][appear[phases]])
    return {
        phases: np.nanmean(np.vstack(tc_list), axis=0)
        for phases, tc_list in tcs.items()
    }


@task(groups=meta_session.groups, cache_saves="tc_appear_mean_normalized")
def cache_combined_tc_appear_mean_normalized(
    infos, group_name, *, all_tc_fields_appear, all_u_tcs_byphase
):
    tcs = {phases: [] for phases in meta.phases_corr}
    for u_tcs_byphase, appear in zip(all_u_tcs_byphase, all_tc_fields_appear):
        for phases in meta.phases_corr:
            tcs[phases].append(
                [
                    tc / np.nansum(tc)
                    for tc in u_tcs_byphase[f"phase{phases[-1]}"][appear[phases]]
                ]
            )
    return {
        phases: np.nanmean(np.vstack([tc for tc in tc_list if len(tc) > 0]), axis=0)
        for phases, tc_list in tcs.items()
    }


@task(infos=meta_session.all_infos, cache_saves="tc_disappear_mean")
def cache_tc_disappear_mean(info, *, tc_fields_disappear, u_tcs_byphase):
    return {
        phases: np.nanmean(
            u_tcs_byphase[f"phase{phases[-2]}"][tc_fields_disappear[phases]], axis=0
        )
        for phases in meta.phases_corr
    }


@task(infos=meta_session.all_infos, cache_saves="tc_disappear_maxpeaks")
def cache_tc_disappear_maxpeaks(info, *, tc_fields_disappear, u_tcs_byphase):
    return {
        phases: np.histogram(
            np.nanargmax(
                u_tcs_byphase[f"phase{phases[-2]}"][tc_fields_disappear[phases]], axis=1
            ),
            bins=meta.linear_bin_edges,
        )[0]
        if np.sum(tc_fields_disappear[phases]) > 0
        else np.zeros(100)
        for phases in meta.phases_corr
    }


@task(groups=meta_session.analysis_grouped, cache_saves="tc_disappear_maxpeaks")
def cache_combined_tc_disappear_maxpeaks(
    infos, group_name, *, all_tc_disappear_maxpeaks
):
    return {
        phases: np.sum(maxpeaks[phases] for maxpeaks in all_tc_disappear_maxpeaks)
        for phases in meta.phases_corr
    }


@task(groups=meta_session.groups, cache_saves="tc_disappear_correlations")
def cache_combined_tc_disappear_correlations(
    infos, group_name, *, all_tc_fields_disappear, all_u_tcs_byphase
):
    correlations = {
        phases: np.zeros((meta.linear_bin_centers.size, meta.linear_bin_centers.size))
        for phases in meta.phases_corr
    }

    for phases in meta.phases_corr:
        tcs_byphase = np.vstack(
            tcs[f"phase{phases[-2]}"][disappear[phases]]
            for tcs, disappear in zip(all_u_tcs_byphase, all_tc_fields_disappear)
        )
        for i in range(meta.linear_bin_centers.size):
            for j in range(meta.linear_bin_centers.size):
                short = ["short_standard", "day2", "day3", "day4"]
                if group_name in short and (i < 20 or j < 20):
                    correlations[phases][i, j] = np.nan
                else:
                    left = tcs_byphase[:, i]
                    right = tcs_byphase[:, j]
                    valid = (~np.isnan(left)) & (~np.isnan(right))
                    if np.sum(valid) >= 2:
                        corr, _ = scipy.stats.pearsonr(left[valid], right[valid])
                        correlations[phases][i, j] = 0 if np.isnan(corr) else corr

    return correlations


@task(infos=meta_session.all_infos, cache_saves="tc_disappear_mean_normalized")
def cache_tc_disappear_mean_normalized(info, *, tc_fields_disappear, u_tcs_byphase):
    return {
        phases: np.nanmean(
            np.vstack(
                [
                    tc / np.nansum(tc)
                    for tc in u_tcs_byphase[f"phase{phases[-2]}"][
                        tc_fields_disappear[phases]
                    ]
                ]
            )
            if np.sum(tc_fields_disappear[phases]) > 0
            else [],
            axis=0,
        )
        for phases in meta.phases_corr
    }


@task(groups=meta_session.groups, cache_saves="tc_disappear_mean")
def cache_combined_tc_disappear_mean(
    infos, group_name, *, all_tc_fields_disappear, all_u_tcs_byphase
):
    tcs = {phases: [] for phases in meta.phases_corr}
    for u_tcs_byphase, disappear in zip(all_u_tcs_byphase, all_tc_fields_disappear):
        for phases in meta.phases_corr:
            tcs[phases].append(u_tcs_byphase[f"phase{phases[-2]}"][disappear[phases]])
    return {
        phases: np.nanmean(np.vstack([tc for tc in tc_list if len(tc) > 0]), axis=0)
        for phases, tc_list in tcs.items()
    }


@task(groups=meta_session.groups, cache_saves="tc_disappear_mean_normalized")
def cache_combined_tc_disappear_mean_normalized(
    infos, group_name, *, all_tc_fields_disappear, all_u_tcs_byphase
):
    tcs = {phases: [] for phases in meta.phases_corr}
    for u_tcs_byphase, disappear in zip(all_u_tcs_byphase, all_tc_fields_disappear):
        for phases in meta.phases_corr:
            tcs[phases].append(
                [
                    tc / np.nansum(tc)
                    for tc in u_tcs_byphase[f"phase{phases[-2]}"][disappear[phases]]
                ]
            )
    return {
        phases: np.nanmean(np.vstack([tc for tc in tc_list if len(tc) > 0]), axis=0)
        for phases, tc_list in tcs.items()
    }


@task(infos=meta_session.all_infos, cache_saves="tc_correlations_within_phase")
def cache_tc_correlations_within_phase(info, *, u_tcs_byphase):
    correlations = {
        phase: np.zeros((meta.linear_bin_centers.size, meta.linear_bin_centers.size))
        for phase in meta.run_times
    }
    for phase in meta.run_times:
        for i in range(meta.linear_bin_centers.size):
            for j in range(meta.linear_bin_centers.size):
                if not info.full_standard_maze and (i < 20 or j < 20):
                    correlations[phase][i, j] = np.nan
                else:
                    left = u_tcs_byphase[phase][:, i]
                    right = u_tcs_byphase[phase][:, j]
                    valid = (~np.isnan(left)) & (~np.isnan(right))
                    if np.sum(valid) >= 2:
                        correlations[phase][i, j], _ = scipy.stats.pearsonr(
                            left[valid], right[valid]
                        )
    return correlations


@task(groups=meta_session.groups, cache_saves="tc_correlations_within_phase")
def cache_combined_tc_correlations_within_phase(
    infos, group_name, *, all_u_tcs_byphase
):
    correlations = {
        phase: np.zeros((meta.linear_bin_centers.size, meta.linear_bin_centers.size))
        for phase in meta.run_times
    }

    for phase in meta.run_times:
        tcs_byphase = np.vstack(tcs[phase] for tcs in all_u_tcs_byphase)
        for i in range(meta.linear_bin_centers.size):
            for j in range(meta.linear_bin_centers.size):
                short = ["short_standard", "day2", "day3", "day4"]
                if group_name in short and (i < 20 or j < 20):
                    correlations[phase][i, j] = np.nan
                else:
                    left = tcs_byphase[:, i]
                    right = tcs_byphase[:, j]
                    valid = (~np.isnan(left)) & (~np.isnan(right))
                    if np.sum(valid) >= 2:
                        corr, _ = scipy.stats.pearsonr(left[valid], right[valid])
                        correlations[phase][i, j] = 0 if np.isnan(corr) else corr

    return correlations
