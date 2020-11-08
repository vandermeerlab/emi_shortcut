import nept
import numpy as np
import scipy.interpolate

import meta
import meta_session
from tasks import task


def get_decoded_position(task_times, tuning_curves, spikes, bin_centers):
    counts = nept.bin_spikes(
        spikes,
        task_times["prerecord"].start,
        task_times["postrecord"].stop,
        dt=meta.decoding_dt,
        window=meta.decoding_window,
        gaussian_std=meta.counts_gaussian,
        normalized=False,
    )
    likelihood = nept.bayesian_prob(
        counts,
        tuning_curves,
        binsize=meta.decoding_dt,
        min_neurons=meta.min_decoding_neurons,
        min_spikes=meta.min_decoding_spikes,
    )
    decoded = nept.decode_location(likelihood, bin_centers, counts.time)
    likelihood = nept.AnalogSignal(
        likelihood[np.sum(np.isnan(likelihood), axis=1) < likelihood.shape[1]],
        decoded.time,
    )
    assert likelihood.dimensions == bin_centers.size
    return decoded, likelihood


@task(
    infos=meta_session.all_infos, cache_saves=["decoded_matched", "likelihood_matched"]
)
def cache_decoded_matched(
    info, *, task_times, matched_tuning_curves, matched_tc_spikes
):
    decoded = {}
    likelihood = {}
    for trajectory in meta.trajectories:
        decoded[trajectory], likelihood[trajectory] = get_decoded_position(
            task_times,
            matched_tuning_curves[trajectory],
            matched_tc_spikes[trajectory],
            meta.linear_bin_centers,
        )
    return {"decoded_matched": decoded, "likelihood_matched": likelihood}


@task(infos=meta_session.all_infos, cache_saves=["decoded", "likelihood"])
def cache_decoded(info, *, task_times, tuning_curves, tc_spikes):
    decoded = {}
    likelihood = {}
    for trajectory in meta.trajectories:
        decoded[trajectory], likelihood[trajectory] = get_decoded_position(
            task_times,
            tuning_curves[trajectory],
            tc_spikes[trajectory],
            meta.linear_bin_centers,
        )
    return {"decoded": decoded, "likelihood": likelihood}


@task(
    infos=meta_session.all_infos,
    cache_saves=["joined_decoded", "joined_replay_likelihood"],
)
def cache_joined_replay_likelihood(
    info, *, task_times, joined_tuning_curves, joined_tc_spikes, joined_replays
):
    decoded, likelihood = get_decoded_position(
        task_times,
        joined_tuning_curves,
        joined_tc_spikes,
        meta.linear_bin_centers,
    )
    return {
        "joined_decoded": decoded,  # TODO: only for replays or everywhere?
        "joined_replay_likelihood": likelihood[joined_replays],
    }


@task(infos=meta_session.all_infos, cache_saves="joined_likelihood_sum_byphase")
def cache_joined_likelihood_sum_byphase(info, *, task_times, joined_replay_likelihood):
    return {
        trajectory: {
            phase: np.sum(
                joined_replay_likelihood[task_times[phase]].data[
                    :, slice(None, 50) if trajectory == "u" else slice(50, None)
                ]
            )
            for phase in meta.task_times
        }
        for trajectory in meta.trajectories
    }


@task(
    groups=meta_session.analysis_grouped,
    savepath=("decoding", "mean_replay_likelihood_bybin.tex"),
)
def save_joined_replay_likelihood_bybin(
    infos,
    group_name,
    *,
    joined_replay_likelihood_bybin,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% Mean likelihood", file=fp)
        print(
            fr"\def \meanulikelihood/{{{np.mean(joined_replay_likelihood_bybin[:50]):.3f}}}",
            file=fp,
        )
        print(
            fr"\def \meanfullshortcutlikelihood/{{{np.mean(joined_replay_likelihood_bybin[50:]):.3f}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(
    infos=meta_session.all_infos, cache_saves="joined_shuffled_likelihood_sum_byphase"
)
def cache_joined_shuffled_likelihood_sum_byphase(
    info,
    *,
    task_times,
    joined_tuning_curves,
    joined_tc_spikes,
    joined_replays,
):
    rng = np.random.RandomState(meta.seed)
    shuffled_likelihood = {
        trajectory: {phase: [] for phase in meta.task_times}
        for trajectory in meta.trajectories
    }
    for _ in range(meta.n_likelihood_shuffles if meta.full_shuffle else 2):
        _, likelihood = get_decoded_position(
            task_times,
            joined_tuning_curves[
                rng.choice(
                    joined_tuning_curves.shape[0],
                    size=len(joined_tuning_curves),
                    replace=False,
                )
            ],
            joined_tc_spikes,
            meta.linear_bin_centers,
        )
        likelihood = likelihood[joined_replays]
        for trajectory in meta.trajectories:
            for phase in meta.task_times:
                shuffled_likelihood[trajectory][phase].append(
                    np.sum(
                        likelihood[task_times[phase]].data[
                            :, slice(None, 50) if trajectory == "u" else slice(50, None)
                        ]
                    )
                )
    return shuffled_likelihood


@task(
    infos=meta_session.all_infos,
    cache_saves=["zscored_logodds", "shuffled_zscored_logodds"],
)
def cache_zscored_logodds(
    info, *, joined_likelihood_sum_byphase, joined_shuffled_likelihood_sum_byphase
):
    zscored_logodds = {}
    shuffled_zscored_logodds = {}
    logodds = {phase: [] for phase in meta.task_times}
    for phase in meta.task_times:
        logodds[phase].append(
            np.log10(
                joined_likelihood_sum_byphase["full_shortcut"][phase]
                / joined_likelihood_sum_byphase["u"][phase]
            )
        )
        for shuffled_full_shortcut, shuffled_u in zip(
            joined_shuffled_likelihood_sum_byphase["full_shortcut"][phase],
            joined_shuffled_likelihood_sum_byphase["u"][phase],
        ):
            logodds[phase].append(np.log10(shuffled_full_shortcut / shuffled_u))

        zscored = scipy.stats.zscore(logodds[phase])
        zscored_logodds[phase] = zscored[0]
        shuffled_zscored_logodds[phase] = zscored[1:]

    return {
        "zscored_logodds": zscored_logodds,
        "shuffled_zscored_logodds": shuffled_zscored_logodds,
    }


@task(groups=meta_session.groups, cache_saves="zscored_logodds")
def cache_combined_zscored_logodds(infos, group_name, *, all_zscored_logodds):
    return {
        phase: [zscored_logodds[phase] for zscored_logodds in all_zscored_logodds]
        for phase in meta.task_times
    }


def get_aligned_position(linear, decoded):
    f_xy = scipy.interpolate.interp1d(
        linear.time,
        linear.data.T,
        kind="nearest",
        fill_value="extrapolate",
    )
    return nept.Position(f_xy(decoded.time)[0], decoded.time)


@task(infos=meta_session.all_infos, cache_saves="aligned_position")
def cache_aligned_position(info, *, linear, decoded):
    return {
        trajectory: get_aligned_position(linear[trajectory], decoded[trajectory])
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="decoding_error")
def cache_decoding_error(info, *, task_times, linear, decoded, aligned_position):
    error = {}
    for trajectory in meta.trajectories:
        run_epoch = nept.run_threshold(
            linear[trajectory][task_times["maze_times"]],
            thresh=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )
        aligned = aligned_position[trajectory][run_epoch]
        error[trajectory] = nept.AnalogSignal(
            aligned.distance(decoded[trajectory][run_epoch]), aligned.time
        )
    return error


@task(groups=meta_session.groups, cache_saves="decoding_error")
def cache_combined_decoding_error(infos, group_name, *, all_decoding_error):
    return {
        trajectory: np.hstack(
            [
                decoding_error[trajectory].data[:, 0]
                for decoding_error in all_decoding_error
            ]
        )
        for trajectory in meta.trajectories
    }


@task(
    groups=meta_session.analysis_grouped, savepath=("decoding", "decoding_errors.tex")
)
def save_decoding_errors(
    infos,
    group_name,
    *,
    decoding_error,
    all_decoding_error,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% Decoding errors", file=fp)
        for info, this_error in zip(infos, all_decoding_error):
            print(f"% {info.session_id}", file=fp)
            for trajectory in meta.trajectories:
                print(
                    f"% {trajectory} mean decoding error: "
                    f"{np.mean(this_error[trajectory].data):.4f}",
                    file=fp,
                )
                print(
                    f"% {trajectory} median decoding error: "
                    f"{np.median(this_error[trajectory].data):.4f}",
                    file=fp,
                )
            print("% ---------", file=fp)
        print("% Combined", file=fp)
        for trajectory in meta.trajectories:
            traj = trajectory.replace("_", "")
            print(
                fr"\def \meanerror{traj}/{{{np.mean(decoding_error[trajectory]):.1f}}}",
                file=fp,
            )
            print(
                f"% {trajectory} median decoding error: "
                f"{np.median(decoding_error[trajectory]):.1f}",
                file=fp,
            )


@task(infos=meta_session.all_infos, cache_saves="decoding_error_bybin")
def cache_decoding_error_bybin(info, *, linear, aligned_position, decoding_error):
    decoding_error_bybin = {}
    for trajectory in meta.trajectories:
        error_bybin = [[] for _ in range(meta.linear_bin_centers.size)]
        run_epoch = nept.run_threshold(
            linear[trajectory],
            thresh=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )
        for aligned_x, error in zip(
            aligned_position[trajectory][run_epoch].x, decoding_error[trajectory].data
        ):
            idx = nept.find_nearest_idx(meta.linear_bin_centers, aligned_x)
            error_bybin[idx].append(error.item())
        decoding_error_bybin[trajectory] = error_bybin
    return decoding_error_bybin


@task(infos=meta_session.all_infos, cache_saves="mean_error_bybin")
def cache_mean_error_bybin(info, *, decoding_error_bybin):
    return {
        trajectory: np.array(
            [
                np.nan if len(error_bin) == 0 else np.nanmean(error_bin)
                for error_bin in decoding_error_bybin[trajectory]
            ]
        )
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="mean_error_bybin")
def cache_combined_mean_error_bybin(infos, group_name, *, all_decoding_error_bybin):
    mean_error_bybin = {}
    for trajectory in meta.trajectories:
        error_bybin = [[] for _ in range(meta.linear_bin_centers.size)]
        for decoding_error_bybin in all_decoding_error_bybin:
            for this_bin, error_bin in zip(
                decoding_error_bybin[trajectory], error_bybin
            ):
                error_bin.extend(this_bin)
        mean_error_bybin[trajectory] = np.array(
            [
                np.nan if len(error_bin) == 0 else np.nanmean(error_bin)
                for error_bin in error_bybin
            ]
        )
    return mean_error_bybin


@task(infos=meta_session.all_infos, cache_saves="decoding_occupancy")
def cache_decoding_occupancy(info, *, decoding_error_bybin):
    return {
        trajectory: [len(error_bin) for error_bin in decoding_error_bybin[trajectory]]
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="decoding_occupancy")
def cache_combined_decoding_occupancy(infos, group_name, *, all_decoding_occupancy):
    return {
        trajectory: np.sum(
            [occupancy[trajectory] for occupancy in all_decoding_occupancy], axis=0
        )
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="decoded_byreplay")
def cache_decoded_byreplay(info, *, decoded, replays):
    return {
        trajectory: [decoded[trajectory][replay] for replay in replays[trajectory]]
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="replay_decoding_bybin")
def cache_replay_decoding_bybin(infos, group_name, *, all_decoded_byreplay):
    return {
        trajectory: np.histogram(
            np.hstack(
                [
                    np.squeeze(replay.data)
                    for decoded_byreplay in all_decoded_byreplay
                    for replay in decoded_byreplay[trajectory]
                ]
            ),
            bins=meta.linear_bin_edges,
        )[0]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="likelihood_byreplay_matched")
def cache_likelihood_byreplay_matched(info, *, likelihood_matched, replays):
    return {
        trajectory: [
            likelihood_matched[trajectory][replay]
            for replay in replays[trajectory]
            if likelihood_matched[trajectory][replay].n_samples > 0
        ]
        for trajectory in meta.trajectories
    }


@task(groups=meta_session.groups, cache_saves="replay_likelihood_bybin")
def cache_combined_replay_likelihood_bybin(
    infos, group_name, *, all_likelihood_byreplay
):
    return {
        trajectory: np.nanmean(
            np.vstack(
                [
                    replay.data
                    for likelihood_byreplay in all_likelihood_byreplay
                    for replay in likelihood_byreplay[trajectory]
                ]
            ),
            axis=0,
        )
        if sum(
            len(likelihood_byreplay) for likelihood_byreplay in all_likelihood_byreplay
        )
        > 0
        else np.ones(100) * np.nan
        for trajectory in meta.trajectories
    }


@task(
    infos=meta_session.analysis_infos,
    cache_saves="replay_likelihood_bybin_byphase_matched",
)
def cache_replay_likelihood_bybin_byphase_matched(
    info, *, task_times, likelihood_byreplay_matched
):
    replay_likelihood_byphase = {
        task_time: {trajectory: [] for trajectory in meta.trajectories}
        for task_time in meta.task_times
    }
    for trajectory in meta.trajectories:
        if len(likelihood_byreplay_matched[trajectory]) > 0:
            for task_time in meta.task_times:
                for replay in likelihood_byreplay_matched[trajectory]:
                    if task_times[task_time].contains(replay.time[0]):
                        replay_likelihood_byphase[task_time][trajectory].append(replay)
    return {
        task_time: {
            trajectory: np.nanmean(
                np.vstack(
                    [
                        replay.data
                        for replay in replay_likelihood_byphase[task_time][trajectory]
                    ]
                ),
                axis=0,
            )
            if len(replay_likelihood_byphase[task_time][trajectory]) > 0
            else np.ones(100) * np.nan
            for trajectory in meta.trajectories
        }
        for task_time in meta.task_times
    }


@task(groups=meta_session.groups, cache_saves="replay_likelihood_bybin_byphase_matched")
def cache_combined_replay_likelihood_bybin_byphase_matched(
    infos, group_name, *, all_task_times, all_likelihood_byreplay_matched
):
    replay_likelihood_byphase = {
        task_time: {trajectory: [] for trajectory in meta.trajectories}
        for task_time in meta.task_times
    }
    for likelihood_byreplay, task_times in zip(
        all_likelihood_byreplay_matched, all_task_times
    ):
        for trajectory in meta.trajectories:
            if len(likelihood_byreplay[trajectory]) > 0:
                for task_time in meta.task_times:
                    for replay in likelihood_byreplay[trajectory]:
                        if task_times[task_time].contains(replay.time[0]):
                            replay_likelihood_byphase[task_time][trajectory].append(
                                replay
                            )
    return {
        task_time: {
            trajectory: np.nanmean(
                np.vstack(
                    [
                        replay.data
                        for replay in replay_likelihood_byphase[task_time][trajectory]
                    ]
                )
                if len(replay_likelihood_byphase[task_time][trajectory]) > 0
                else np.ones(100) * np.nan,
                axis=0,
            )
            for trajectory in meta.trajectories
        }
        for task_time in meta.task_times
    }


@task(infos=meta_session.all_infos, cache_saves="joined_likelihood_byreplay")
def cache_joined_likelihood_byreplay(info, *, joined_replay_likelihood, joined_replays):
    return [joined_replay_likelihood[replay] for replay in joined_replays]


@task(groups=meta_session.groups, cache_saves="joined_replay_likelihood_bybin")
def cache_joined_replay_likelihood_bybin(
    infos, group_name, *, all_joined_likelihood_byreplay
):
    return np.nanmean(
        np.vstack(
            [
                replay.data
                for likelihood_byreplay in all_joined_likelihood_byreplay
                for replay in likelihood_byreplay
            ]
        ),
        axis=0,
    )


@task(infos=meta_session.all_infos, cache_saves="likelihood_byreplay")
def cache_likelihood_byreplay(info, *, likelihood, replays):
    return {
        trajectory: [likelihood[trajectory][replay] for replay in replays[trajectory]]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.analysis_infos, cache_saves="replay_likelihood_bybin")
def cache_replay_likelihood_bybin(info, *, likelihood_byreplay):
    return {
        trajectory: np.nanmean(
            np.vstack([replay.data for replay in likelihood_byreplay[trajectory]]),
            axis=0,
        )
        if len(likelihood_byreplay[trajectory]) > 0
        else np.ones(100) * np.nan
        for trajectory in meta.trajectories
    }


@task(
    infos=meta_session.analysis_infos,
    cache_saves="replay_likelihood_bybin_byphase",
)
def cache_replay_likelihood_bybin_byphase(info, *, task_times, likelihood_byreplay):
    replay_likelihood_byphase = {
        task_time: {trajectory: [] for trajectory in meta.trajectories}
        for task_time in meta.task_times
    }
    for trajectory in meta.trajectories:
        if len(likelihood_byreplay[trajectory]) > 0:
            for task_time in meta.task_times:
                for likelihood in likelihood_byreplay[trajectory]:
                    if likelihood.time.shape[0] > 0:
                        if task_times[task_time].contains(likelihood.time[0]):
                            replay_likelihood_byphase[task_time][trajectory].append(
                                likelihood
                            )
    return {
        task_time: {
            trajectory: np.nanmean(
                np.vstack(
                    [
                        replay.data
                        for replay in replay_likelihood_byphase[task_time][trajectory]
                    ]
                ),
                axis=0,
            )
            if len(replay_likelihood_byphase[task_time][trajectory]) > 0
            else np.ones(100) * np.nan
            for trajectory in meta.trajectories
        }
        for task_time in meta.task_times
    }


@task(groups=meta_session.groups, cache_saves="replay_likelihood_bybin_byphase")
def cache_combined_replay_likelihood_bybin_byphase(
    infos, group_name, *, all_task_times, all_likelihood_byreplay
):
    replay_likelihood_byphase = {
        task_time: {trajectory: [] for trajectory in meta.trajectories}
        for task_time in meta.task_times
    }
    for likelihood_byreplay, task_times in zip(all_likelihood_byreplay, all_task_times):
        for trajectory in meta.trajectories:
            if len(likelihood_byreplay[trajectory]) > 0:
                for task_time in meta.task_times:
                    for likelihood in likelihood_byreplay[trajectory]:
                        if likelihood.time.shape[0] > 0:
                            if task_times[task_time].contains(likelihood.time[0]):
                                replay_likelihood_byphase[task_time][trajectory].append(
                                    likelihood
                                )
    return {
        task_time: {
            trajectory: np.nanmean(
                np.vstack(
                    [
                        replay.data
                        for replay in replay_likelihood_byphase[task_time][trajectory]
                    ]
                )
                if len(replay_likelihood_byphase[task_time][trajectory]) > 0
                else np.ones(100) * np.nan,
                axis=0,
            )
            for trajectory in meta.trajectories
        }
        for task_time in meta.task_times
    }


@task(
    infos=meta_session.analysis_infos,
    cache_saves="joined_replay_likelihood_bybin_byphase",
)
def cache_joined_replay_likelihood_bybin_byphase(
    info, *, task_times, joined_likelihood_byreplay
):
    replay_likelihood_byphase = {task_time: [] for task_time in meta.task_times}
    if len(joined_likelihood_byreplay) > 0:
        for task_time in meta.task_times:
            for likelihood in joined_likelihood_byreplay:
                if likelihood.time.shape[0] > 0:
                    if task_times[task_time].contains(likelihood.time[0]):
                        replay_likelihood_byphase[task_time].append(likelihood)
    return {
        task_time: np.nanmean(
            np.vstack([replay.data for replay in replay_likelihood_byphase[task_time]]),
            axis=0,
        )
        if len(replay_likelihood_byphase[task_time]) > 0
        else np.ones(100) * np.nan
        for task_time in meta.task_times
    }


@task(groups=meta_session.groups, cache_saves="joined_replay_likelihood_bybin_byphase")
def cache_combined_joined_replay_likelihood_bybin_byphase(
    infos, group_name, *, all_task_times, all_joined_likelihood_byreplay
):
    replay_likelihood_byphase = {task_time: [] for task_time in meta.task_times}
    for likelihood_byreplay, task_times in zip(
        all_joined_likelihood_byreplay, all_task_times
    ):
        if len(likelihood_byreplay) > 0:
            for task_time in meta.task_times:
                for likelihood in likelihood_byreplay:
                    if likelihood.time.shape[0] > 0:
                        if task_times[task_time].contains(likelihood.time[0]):
                            replay_likelihood_byphase[task_time].append(likelihood)
    return {
        task_time: np.nanmean(
            np.vstack([replay.data for replay in replay_likelihood_byphase[task_time]])
            if len(replay_likelihood_byphase[task_time]) > 0
            else np.ones(100) * np.nan,
            axis=0,
        )
        for task_time in meta.task_times
    }


@task(groups=meta_session.analysis_grouped, savepath=("decoding", "excluded_bins.tex"))
def save_excluded_bins(
    infos, group_name, *, all_task_times, all_decoded, all_matched_linear, savepath
):
    with open(savepath, "w") as fp:
        print("% Number of excluded bins", file=fp)

        for info, task_times, decoded, linear in zip(
            infos, all_task_times, all_decoded, all_matched_linear
        ):
            print(f"% {info.session_id}", file=fp)

            edges = nept.get_edges(
                task_times["prerecord"].start,
                task_times["postrecord"].stop,
                binsize=meta.decoding_dt,
                lastbin=False,
            )[:-1]
            possible_bins = nept.AnalogSignal(edges, edges)[task_times["maze_times"]]
            n_possible_bins = possible_bins.n_samples
            for trajectory in meta.trajectories:
                this_decoded = decoded[trajectory][task_times["maze_times"]]
                n_decoded_bins = this_decoded.n_samples
                print(
                    f"% Bins excluded for not enough '{trajectory}' neurons: "
                    f"{n_possible_bins - n_decoded_bins} / {n_possible_bins}",
                    file=fp,
                )
                run_epoch = nept.run_threshold(
                    linear[trajectory][task_times["maze_times"]],
                    thresh=meta.std_speed_limit,
                    t_smooth=meta.std_t_smooth,
                )
                n_final_bins = this_decoded[run_epoch].n_samples
                print(
                    f"% Bins excluded for speed thresholding: "
                    f"{n_decoded_bins - n_final_bins} / {n_decoded_bins}",
                    file=fp,
                )
                print(
                    f"% Final bins included: {n_final_bins} / {n_possible_bins}",
                    file=fp,
                )
            print("% ---------", file=fp)
