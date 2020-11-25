import os

import matplotlib.pyplot as plt
import nept
import numpy as np
import scipy.stats

import meta
import meta_session
import paths
from plots import (
    plot_bar_mean_byphase,
    plot_both_by_standard_position,
    plot_raster,
    plot_replay_metric,
    significance_bar,
)
from tasks import task
from utils import mannwhitneyu


@task(infos=meta_session.all_infos, write_example_plots="swrs")
def plot_swrs(
    info,
    *,
    matched_tuning_curves,
    matched_tc_spikes,
    swrs,
    swr_correlations,
    swr_correlations_p,
    swr_correlation_percentiles,
    replays_idx,
    position,
    lfp_swr,
    task_times,
    example_plots,
):
    def plot(trajectory, i, buffer=meta.swr_buffer, show_corr=False):
        swr = swrs[i]
        start = swr.start - buffer
        stop = swr.stop + buffer
        for task_time in meta.task_times:
            if task_times[task_time].contains(swr.centers):
                break
        else:
            assert all(i not in r_idx for r_idx in replays_idx.values())

        correlation = swr_correlations[trajectory][i]
        if np.isnan(correlation):
            return
        replay = "replays" if i in replays_idx[trajectory] else "swrs"
        swr_spikes = [
            spiketrain.time_slice(start, stop)
            for spiketrain in matched_tc_spikes[trajectory]
        ]
        if show_corr:
            plot_raster(
                swr_spikes,
                (start, stop),
                position=position,
                lfp=lfp_swr.time_slice(start, stop),
                buffer=buffer,
                tuning_curves=matched_tuning_curves[trajectory],
                correlation=correlation,
                correlation_p=swr_correlations_p[trajectory][i],
                percentile=swr_correlation_percentiles[trajectory][i],
                savepath=example_plots["swrs"].savepath(
                    info, trajectory, i, task_time, replay
                ),
            )
        else:
            plot_raster(
                swr_spikes,
                (start, stop),
                lfp=lfp_swr.time_slice(start, stop),
                buffer=buffer,
                tuning_curves=matched_tuning_curves[trajectory],
                savepath=example_plots["swrs"].savepath(
                    info, trajectory, i, task_time, replay
                ),
            )

    if meta.plot_all:
        for i in range(swrs.n_epochs):
            for trajectory in meta.trajectories:
                plot(trajectory, i, show_corr=True)
    else:
        for trajectory, i, _, _, _ in example_plots["swrs"].zip(info):
            plot(trajectory, i)


@task(infos=meta_session.all_infos, write_example_plots="swrs_without_tc")
def plot_swrs_without_tuning_curves(
    info,
    *,
    matched_tc_spikes,
    swrs,
    swr_correlations,
    swr_correlations_p,
    swr_correlation_percentiles,
    replays_idx,
    position,
    lfp_swr,
    task_times,
    example_plots,
):
    def plot(trajectory, i, buffer=meta.swr_buffer, show_corr=False):
        swr = swrs[i]
        start = swr.start - buffer
        stop = swr.stop + buffer
        for task_time in meta.task_times:
            if task_times[task_time].contains(swr.centers):
                break
        else:
            assert all(i not in r_idx for r_idx in replays_idx.values())

        correlation = swr_correlations[trajectory][i]
        if np.isnan(correlation):
            return
        replay = (
            "replays-without-tc" if i in replays_idx[trajectory] else "swrs-without-tc"
        )
        swr_spikes = [
            spiketrain.time_slice(start, stop)
            for spiketrain in matched_tc_spikes[trajectory]
        ]
        if show_corr:
            plot_raster(
                swr_spikes,
                (start, stop),
                position=position,
                lfp=lfp_swr.time_slice(start, stop),
                buffer=buffer,
                tuning_curves=None,
                correlation=correlation,
                correlation_p=swr_correlations_p[trajectory][i],
                percentile=swr_correlation_percentiles[trajectory][i],
                savepath=example_plots["swrs_without_tc"].savepath(
                    info, trajectory, i, task_time, replay
                ),
            )
        else:
            plot_raster(
                swr_spikes,
                (start, stop),
                lfp=lfp_swr.time_slice(start, stop),
                buffer=buffer,
                tuning_curves=None,
                savepath=example_plots["swrs_without_tc"].savepath(
                    info, trajectory, i, task_time, replay
                ),
            )

    if meta.plot_all:
        for i in range(swrs.n_epochs):
            for trajectory in meta.trajectories:
                plot(trajectory, i, show_corr=True)
    else:
        for trajectory, i, _, _, _ in example_plots["swrs_without_tc"].zip(info):
            plot(trajectory, i)


@task(
    infos=meta_session.analysis_infos, read_example_plots=["swrs", "matched_run_raster"]
)
def plot_swr_and_matched_run_raster(
    info,
    *,
    trials,
    matched_tuning_curves,
    matched_tc_spikes,
    swrs,
    lfp_swr,
    example_plots,
):
    for trajectory, run_idx, _ in example_plots["matched_run_raster"].zip(info):
        for swr_trajectory, swr_idx, _, _, _ in example_plots["swrs"].zip(info):
            if trajectory != swr_trajectory:
                continue
            swr_buffer = 0.015
            trial = trials[trajectory][run_idx]
            swr = swrs[swr_idx]
            swr_start = swr.start - swr_buffer
            swr_stop = swr.stop + swr_buffer

            savepath = paths.plot_file(
                f"ind-{info.session_id}",
                "ind-swr-run-raster",
                f"{trajectory}-run-{run_idx}-swr-{swr_idx}-raster.svg",
            )
            os.makedirs(os.path.dirname(savepath), exist_ok=True)

            plot_raster(
                spikes=[
                    spiketrain.time_slice(trial.start, trial.stop)
                    for spiketrain in matched_tc_spikes[trajectory]
                ],
                xlim=(trial.start, trial.stop),
                tuning_curves=matched_tuning_curves[trajectory],
                swr_raster=[
                    spiketrain.time_slice(swr_start, swr_stop)
                    for spiketrain in matched_tc_spikes[trajectory]
                ],
                swr_lfp=lfp_swr.time_slice(swr_start, swr_stop),
                swr_buffer=swr_buffer,
                savepath=savepath,
            )


@task(
    groups=meta_session.analysis_grouped, savepath=("swrs", "swr_durations_byphase.svg")
)
def plot_swr_durations_byphase(infos, group_name, *, swr_durations_byphase, savepath):
    colors = {"rest": "#bdbdbd", "run": "#737373"}
    x = np.arange(len(meta.task_times))
    width = 0.65

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(
        x,
        [np.mean(swr_durations_byphase[phase]) * 1000 for phase in meta.task_times],
        width,
        color=[colors["run"] if i % 2 else colors["rest"] for i in range(7)],
        yerr=[
            scipy.stats.sem(swr_durations_byphase[phase]) for phase in meta.task_times
        ],
        ecolor="k",
    )
    plt.xticks(x, list(meta.task_times_labels.values()), fontsize=meta.fontsize)
    plt.ylabel("Mean SWR duration (ms)", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    groups=meta_session.analysis_grouped,
    savepath=("swrs", "swr_durations_histogram.svg"),
)
def plot_swr_durations_histogram(infos, group_name, *, swrs_durations, savepath):
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.hist(np.array(swrs_durations) * 1000, bins=20, color="#969696")
    plt.xticks(fontsize=meta.fontsize)
    plt.xlabel("SWR duration (ms)", fontsize=meta.fontsize)
    plt.ylabel("Number of events", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    # ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1e"))
    ax.ticklabel_format(axis="y", style="plain")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        trajectory: ("replays", f"replay_durations_histogram_{trajectory}.svg")
        for trajectory in meta.trajectories
    },
)
def plot_replay_durations_histogram(infos, group_name, *, replay_durations, savepath):
    for trajectory in meta.trajectories:
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.hist(
            np.array(replay_durations[trajectory]) * 1000,
            bins=20,
            color=meta.colors[trajectory],
        )
        plt.xticks(fontsize=meta.fontsize)
        plt.xlabel("Replay duration (ms)", fontsize=meta.fontsize)
        plt.ylabel("Number of events", fontsize=meta.fontsize)
        plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
        plt.axvline(
            np.mean(replay_durations[trajectory]) * 1000, linestyle="dashed", color="k"
        )
        plt.xlim(0, 420)
        plt.ylim(0, 820)
        plt.title(f"{meta.trajectories_labels[trajectory]}", fontsize=meta.fontsize)

        # ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.1e"))
        ax.ticklabel_format(axis="y", style="plain")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")

        plt.tight_layout(h_pad=0.003)

        plt.savefig(savepath[trajectory], bbox_inches="tight", transparent=True)
        plt.close(fig)


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        "full": ("swrs", "swr_rate_byphase_full.svg"),
        "rest": ("swrs", "swr_rate_byphase_rest.svg"),
    },
)
def plot_swr_rate_byphase(
    infos,
    group_name,
    *,
    swr_rate_byphase,
    swr_rate_byphase_restonly,
    swr_n_byphase,
    swr_n_byphase_restonly,
    savepath,
):
    plot_bar_mean_byphase(
        {phase: np.array(swr_rate_byphase[phase]) * 60 for phase in meta.task_times},
        n_byphase=swr_n_byphase,
        n_sessions=len(infos),
        ylabel="Mean SWR rates (events/min)",
        savepath=savepath["full"],
    )
    plot_bar_mean_byphase(
        {
            phase: np.array(swr_rate_byphase_restonly[phase]) * 60
            for phase in meta.task_times
        },
        n_byphase=swr_n_byphase_restonly,
        n_sessions=len(infos),
        ylabel="Mean SWR rates (events/min)",
        savepath=savepath["rest"],
    )


@task(infos=meta_session.all_infos, savepath=("swrs", "swr_position.svg"))
def plot_swrs_byzone(info, *, position, swrs_byzone, savepath):
    fig = plt.figure()
    plt.plot(position.x, position.y, "k.", alpha=0.2, ms=0.5, rasterized=True)
    for trajectory in meta.all_zones:
        swr_idxs = []
        for center in swrs_byzone[trajectory].centers:
            swr_idxs.append(nept.find_nearest_idx(position.time, center))

        plt.plot(
            position.x[swr_idxs],
            position.y[swr_idxs],
            "o",
            mec="k",
            mew=0.2,
            color=meta.colors[trajectory],
            rasterized=True,
            label=trajectory,
        )

    plt.legend(loc="best", fontsize=meta.fontsize_small)
    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True, dpi=meta.rasterize_dpi)
    plt.close(fig)


@task(
    groups=meta_session.groups,
    savepath={
        "full": ("swrs", "swr_by_std_counts_full.svg"),
        "rest": ("swrs", "swr_by_std_counts_rest.svg"),
    },
)
def plot_swrs_bybin(
    infos,
    group_name,
    *,
    swrs_bybin,
    swrs_bybin_restonly,
    swr_occupancy_bybin,
    swr_occupancy_bybin_restonly,
    savepath,
):
    plot_both_by_standard_position(
        swrs_bybin,
        ylabel="SWR counts",
        metric=swr_occupancy_bybin,
        ymetric="Occupancy",
        savepath=savepath["full"],
    )
    plot_both_by_standard_position(
        swrs_bybin_restonly,
        ylabel="SWR counts",
        metric=swr_occupancy_bybin_restonly,
        ymetric="Occupancy",
        savepath=savepath["rest"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        "full": ("swrs", "swr_by_std_rate_full.svg"),
        "rest": ("swrs", "swr_by_std_rate_rest.svg"),
    },
)
def plot_swr_rate_bybin(
    infos,
    group_name,
    *,
    swr_rate_bybin,
    swr_rate_bybin_restonly,
    savepath,
):
    plot_both_by_standard_position(
        {trajectory: swr_rate_bybin[trajectory] * 60 for trajectory in swr_rate_bybin},
        ylabel="SWR rate (events/min)",
        std_axvlines=True,
        ylim=2.6,
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in swr_rate_bybin
        },
        savepath=savepath["full"],
    )
    plot_both_by_standard_position(
        {
            trajectory: swr_rate_bybin_restonly[trajectory] * 60
            for trajectory in swr_rate_bybin_restonly
        },
        ylabel="SWR rate (events/min)",
        std_axvlines=True,
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in swr_rate_bybin_restonly
        },
        savepath=savepath["rest"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_replays_bybin.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_replays_bybin(infos, group_name, *, replays_bybin, savepath):
    plot_both_by_standard_position(
        replays_bybin,
        ylabel="Replay counts",
        std_axvlines=True,
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in meta.trajectories
        },
        savepath=savepath["overlapping"],
    )
    plot_both_by_standard_position(
        replays_bybin,
        ylabel="Replay counts",
        # ylim=150,
        std_axvlines=True,
        left="only_u",
        right="only_full_shortcut",
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in ["only_u", "only_full_shortcut"]
        },
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_matched_replays_bybin.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_matched_replays_bybin(infos, group_name, *, matched_replays_bybin, savepath):
    plot_both_by_standard_position(
        matched_replays_bybin,
        ylabel="Replay counts",
        std_axvlines=True,
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in meta.trajectories
        },
        savepath=savepath["overlapping"],
    )
    plot_both_by_standard_position(
        matched_replays_bybin,
        ylabel="Replay counts",
        # ylim=150,
        left="only_u",
        right="only_full_shortcut",
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in ["only_u", "only_full_shortcut"]
        },
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_replay_rate_bybin.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_replay_rate_bybin(infos, group_name, *, replay_rate_bybin, savepath):
    replay_rate_bybin = {
        trajectory: replay_rate_bybin[trajectory] * 60
        for trajectory in replay_rate_bybin
    }

    plot_both_by_standard_position(
        replay_rate_bybin,
        ylabel="Replay rate (events/min)",
        savepath=savepath["overlapping"],
    )
    plot_both_by_standard_position(
        replay_rate_bybin,
        ylabel="Replay rate (events/min)",
        left="only_u",
        right="only_full_shortcut",
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        "full": ("swrs", "swr_occupancies_full.svg"),
        "rest": ("swrs", "swr_occupancies_rest.svg"),
    },
)
def plot_swr_occupancies(
    infos,
    group_name,
    *,
    swr_occupancy_bybin,
    swr_occupancy_bybin_restonly,
    savepath,
):
    def plot_occupancy(values_byzone, savepath):
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 5))

        for ax, traj in zip([ax1, ax2], meta.trajectories):
            ax.plot(values_byzone[traj], "o", color=meta.colors[traj])
            ax.tick_params(axis="both", which="major", labelsize=meta.fontsize)
            ax.set_xlabel("Linearized position bins", fontsize=meta.fontsize)
            ax.spines["right"].set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.yaxis.set_ticks_position("left")
            ax.xaxis.set_ticks_position("bottom")

        ax1.set_ylabel("Occupancy (s)", fontsize=meta.fontsize)

        plt.tight_layout(h_pad=0.003)

        plt.savefig(savepath, bbox_inches="tight", transparent=True)
        plt.close(fig)

    plot_occupancy(swr_occupancy_bybin, savepath["full"])
    plot_occupancy(swr_occupancy_bybin_restonly, savepath["rest"])


@task(infos=meta_session.analysis_infos, savepath=("swrs", "swrs_overtime.svg"))
def plot_swrs_overtime(info, *, task_times, swrs_overtime, savepath):
    _plot_swrs_overtime(
        task_times, swrs_overtime, ylabel="Number of events", savepath=savepath
    )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("replays", f"replays_overtime-{traj}.svg") for traj in meta.trajectories
    },
)
def plot_replays_overtime(info, *, task_times, replays_overtime, savepath):
    for trajectory in meta.trajectories:
        _plot_swrs_overtime(
            task_times,
            replays_overtime[trajectory],
            ylabel="Number of events",
            ymax=10.0,
            title=meta.trajectories_labels[trajectory],
            savepath=savepath[trajectory],
        )


def _plot_swrs_overtime(
    task_times, swrs_overtime, ylabel, ymax=None, title=None, savepath=None
):
    task_time_centers = []
    for phase in meta.task_times:
        task_time_centers.append(task_times[phase].centers[0])

    fig, ax = plt.subplots(figsize=(12, 4))

    if ymax is None:
        ymax = np.max(swrs_overtime.data)

    for phase in meta.task_times:
        epoch = task_times[phase]
        if phase in meta.rest_times:
            ax.fill_between(
                [epoch.start, epoch.stop],
                0,
                ymax,
                facecolor="#bdbdbd",
                alpha=0.3,
            )
        if phase in meta.run_times:
            ax.fill_between(
                [epoch.start, epoch.stop],
                0,
                ymax,
                facecolor="#737373",
                alpha=0.3,
            )

    plt.plot(swrs_overtime.time, swrs_overtime.data, color="k")
    plt.ylim(top=ymax)
    plt.locator_params(axis="y", nbins=5)

    if title is not None:
        plt.title(title, fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.set_ticks_position("bottom")

    plt.text(
        0.86,
        1.04,
        s="Example session",
        fontsize=meta.fontsize_small,
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
    )

    # TODO: add swr_overtime_dt to meta?
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    plt.xticks(
        task_time_centers,
        list(meta.task_times_labels.values()),
        rotation=meta.xtickrotation,
        fontsize=meta.fontsize,
    )
    plt.yticks(fontsize=meta.fontsize)

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(infos=meta_session.analysis_infos, savepath=("swrs", "swrs_in_position.svg"))
def plot_swrs_in_position(info, *, task_times, swr_in_position, position, savepath):
    position = position[task_times["maze_times"]]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(
        position.x, position.y, ".", color=meta.colors["rest"], ms=1, rasterized=True
    )
    ax.plot(swr_in_position.x, swr_in_position.y, "ko", ms=6, rasterized=True)

    plt.xlabel("example session")

    plt.axis("off")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True, dpi=meta.rasterize_dpi)
    plt.close(fig)


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        key: ("replays", f"{key}_replay_n_byphase.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_group_replay_n_byphase(infos, group_name, *, replay_n_byphase, savepath):
    plot_replay_metric(
        replay_n_byphase,
        ["u", "full_shortcut"],
        ylabel="Number of replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_n_byphase,
        ["both", "only_u", "only_full_shortcut"],
        ylabel="Number of replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_replay_proportions_byphase.svg")
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_group_replay_proportions_byphase(
    infos,
    group_name,
    *,
    replay_proportions_byphase,
    replay_proportions_byphase_pval,
    savepath,
):
    plot_replay_metric(
        replay_proportions_byphase,
        ["u", "full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        pval=replay_proportions_byphase_pval,
        title=f"{meta.title_labels[group_name]}\n n = {len(infos)} sessions"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byphase,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        pval=replay_proportions_byphase_pval,
        ylim=0.225 if group_name not in ["all", "combined"] else None,
        title=f"{meta.title_labels[group_name]}\n n = {len(infos)} sessions"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byphase,
        ["difference"],
        ylabel="Replay proportion for shortcut - familiar",
        pval=replay_proportions_byphase_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}\n n = {len(infos)} sessions"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byphase,
        ["contrast"],
        ylabel="Replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byphase_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}\n n = {len(infos)} sessions"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["contrast"],
    )


@task(
    infos=meta_session.all_infos,
    savepath={
        key: ("replays", f"{key}_replay_proportions_byphase.svg")
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_replay_proportions_byphase(
    info, *, replay_proportions_byphase, replay_proportions_byphase_pval, savepath
):
    plot_replay_metric(
        replay_proportions_byphase,
        ["u", "full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        pval=replay_proportions_byphase_pval,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byphase,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        pval=replay_proportions_byphase_pval,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byphase,
        ["difference"],
        ylabel="Replay proportion for shortcut - familiar",
        pval=replay_proportions_byphase_pval,
        color_byvalue=True,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byphase,
        ["contrast"],
        ylabel="Replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byphase_pval,
        color_byvalue=True,
        savepath=savepath["contrast"],
    )


@task(
    infos=meta_session.all_infos,
    savepath={
        key: ("replays", f"{key}_replay_n_byphase.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_replay_n_byphase(info, *, replay_n_byphase, savepath):
    plot_replay_metric(
        replay_n_byphase,
        ["u", "full_shortcut"],
        ylabel="Number of replays",
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_n_byphase,
        ["both", "only_u", "only_full_shortcut"],
        ylabel="Number of replays",
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        f"{key}-{trajectory}": (
            "replays",
            f"{key}_replay_proportions_normalized_byphase_{trajectory}.svg",
        )
        for trajectory in meta.trajectories
        for key in ["overlapping", "exclusive"]
    },
)
def plot_replay_proportions_normalized_byphase(
    infos,
    group_name,
    *,
    replay_proportions_normalized_byphase,
    replay_proportions_byphase_pval,
    savepath,
):
    for trajectory in meta.trajectories:
        for key in ["overlapping", "exclusive"]:
            plot_replay_metric(
                replay_proportions_normalized_byphase,
                [f"{'only_' if key == 'exclusive' else ''}{trajectory}"],
                ylabel="Replay proportion /\nmean replay proportion",
                pval=replay_proportions_byphase_pval,
                title=f"{meta.title_labels[group_name]}"
                if group_name not in ["all", "combined"]
                else None,
                savepath=savepath[f"{key}-{trajectory}"],
            )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_replay_n_byexperience.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_group_replay_n_byexperience(
    infos, group_name, *, replay_n_byexperience, savepath
):
    plot_replay_metric(
        replay_n_byexperience,
        ["u", "full_shortcut"],
        ylabel="Number of replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_n_byexperience,
        ["both", "only_u", "only_full_shortcut"],
        ylabel="Number of replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_replay_proportions_byexperience_bytrial.svg")
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_group_replay_proportions_byexperience(
    infos,
    group_name,
    *,
    replay_proportions_byexperience_bytrial,
    replay_proportions_byexperience_bytrial_pval,
    savepath,
):
    plot_replay_metric(
        replay_proportions_byexperience_bytrial,
        ["u", "full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        pval=replay_proportions_byexperience_bytrial_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_bytrial,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        pval=replay_proportions_byexperience_bytrial_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_bytrial,
        ["difference"],
        ylabel="Replay proportion for shortcut - familiar",
        pval=replay_proportions_byexperience_bytrial_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_bytrial,
        ["contrast"],
        ylabel="Replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byexperience_bytrial_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["contrast"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: (
            "replays",
            f"{key}_replay_proportions_byexperience_feederonly_bytrial.svg",
        )
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_group_replay_proportions_byexperience_feederonly_bytrial(
    infos,
    group_name,
    *,
    replay_proportions_byexperience_feederonly_bytrial,
    replay_proportions_byexperience_feederonly_bytrial_pval,
    savepath,
):
    plot_replay_metric(
        replay_proportions_byexperience_feederonly_bytrial,
        ["u", "full_shortcut"],
        ylabel="Proportion of feeder SWRs\nthat are replays",
        pval=replay_proportions_byexperience_feederonly_bytrial_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_feederonly_bytrial,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of feeder SWRs\nthat are replays",
        pval=replay_proportions_byexperience_feederonly_bytrial_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_feederonly_bytrial,
        ["difference"],
        ylabel="Feeder replay proportion for shortcut - familiar",
        pval=replay_proportions_byexperience_feederonly_bytrial_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_feederonly_bytrial,
        ["contrast"],
        ylabel="Feeder replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byexperience_feederonly_bytrial_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["contrast"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays", f"{key}_replay_proportions_byexperience_nofeeder_bytrial.svg")
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_group_replay_proportions_byexperience_nofeeder_bytrial(
    infos,
    group_name,
    *,
    replay_proportions_byexperience_nofeeder_bytrial,
    replay_proportions_byexperience_nofeeder_bytrial_pval,
    savepath,
):
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder_bytrial,
        ["u", "full_shortcut"],
        ylabel="Proportion of path SWRs\nthat are replays",
        pval=replay_proportions_byexperience_nofeeder_bytrial_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder_bytrial,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of path SWRs\nthat are replays",
        pval=replay_proportions_byexperience_nofeeder_bytrial_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder_bytrial,
        ["difference"],
        ylabel="Path replay proportion for shortcut - familiar",
        pval=replay_proportions_byexperience_nofeeder_bytrial_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder_bytrial,
        ["contrast"],
        ylabel="Path replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byexperience_nofeeder_bytrial_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["contrast"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: (
            "replays",
            f"{key}_replay_proportions_byexperience_feederonly.svg",
        )
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_group_replay_proportions_byexperience_feederonly(
    infos,
    group_name,
    *,
    replay_proportions_byexperience_feederonly,
    replay_proportions_byexperience_feederonly_pval,
    savepath,
):
    original_xlabels = meta.on_task
    labels = meta.on_task_labels

    plot_replay_metric(
        replay_proportions_byexperience_feederonly,
        ["u", "full_shortcut"],
        ylabel="Proportion of feeder SWRs\nthat are replays",
        pval=replay_proportions_byexperience_feederonly_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_feederonly,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of feeder SWRs\nthat are replays",
        pval=replay_proportions_byexperience_feederonly_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_feederonly,
        ["difference"],
        ylabel="Feeder replay proportion for shortcut - familiar",
        pval=replay_proportions_byexperience_feederonly_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_feederonly,
        ["contrast"],
        ylabel="Feeder replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byexperience_feederonly_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["contrast"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: (
            "replays",
            f"{key}_replay_proportions_byexperience_nofeeder.svg",
        )
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_group_replay_proportions_byexperience_nofeeder(
    infos,
    group_name,
    *,
    replay_proportions_byexperience_nofeeder,
    replay_proportions_byexperience_nofeeder_pval,
    savepath,
):
    original_xlabels = meta.on_task
    labels = meta.on_task_labels

    plot_replay_metric(
        replay_proportions_byexperience_nofeeder,
        ["u", "full_shortcut"],
        ylabel="Proportion of path SWRs\nthat are replays",
        pval=replay_proportions_byexperience_nofeeder_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of path SWRs\nthat are replays",
        pval=replay_proportions_byexperience_nofeeder_pval,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder,
        ["difference"],
        ylabel="Feeder replay proportion for shortcut - familiar",
        pval=replay_proportions_byexperience_nofeeder_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byexperience_nofeeder,
        ["contrast"],
        ylabel="Feeder replay proportion contrast\nfor shortcut vs familiar",
        pval=replay_proportions_byexperience_nofeeder_pval,
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["contrast"],
    )


@task(
    infos=meta_session.all_infos,
    savepath={
        key: ("replays", f"{key}_replay_proportions_byexperience.svg")
        for key in ["overlapping", "exclusive", "difference", "contrast"]
    },
)
def plot_replay_proportions_byexperience(
    info, *, replay_proportions_byexperience, savepath
):
    plot_replay_metric(
        replay_proportions_byexperience,
        ["u", "full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_proportions_byexperience,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        savepath=savepath["exclusive"],
    )
    plot_replay_metric(
        replay_proportions_byexperience,
        ["difference"],
        ylabel="Replay proportion for shortcut - familiar",
        color_byvalue=True,
        savepath=savepath["difference"],
    )
    plot_replay_metric(
        replay_proportions_byexperience,
        ["contrast"],
        ylabel="Replay proportion contrast\nfor shortcut vs familiar",
        color_byvalue=True,
        savepath=savepath["contrast"],
    )


@task(
    infos=meta_session.all_infos,
    savepath={
        key: ("replays", f"{key}_replay_n_byexperience.svg")
        for key in ["overlapping", "exclusive"]
    },
)
def plot_replay_n_byexperience(info, *, replay_n_byexperience, savepath):
    plot_replay_metric(
        replay_n_byexperience,
        ["u", "full_shortcut"],
        ylabel="Number of replays",
        savepath=savepath["overlapping"],
    )
    plot_replay_metric(
        replay_n_byexperience,
        ["both", "only_u", "only_full_shortcut"],
        ylabel="Number of replays",
        savepath=savepath["exclusive"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        traj: ("swrs", f"correlation_hist-{traj}.svg") for traj in meta.trajectories
    },
)
def plot_swr_correlation_histogram(
    infos,
    group_name,
    *,
    swr_correlations_shuffled,
    swr_correlations,
    swr_correlation_percentiles,
    savepath,
):
    for trajectory in meta.trajectories:
        _plot_swr_correlation_histogram(
            correlations=swr_correlations[trajectory],
            shuffled=swr_correlations_shuffled[trajectory][:, 1:],
            percentiles=swr_correlation_percentiles[trajectory],
            color=meta.colors[trajectory],
            title=meta.trajectories_labels[trajectory],
            savepath=savepath[trajectory],
        )


@task(
    groups=meta_session.groups,
    savepath={
        traj: ("swrs", f"shuffle_correlation_hist-{traj}.svg")
        for traj in meta.trajectories
    },
)
def plot_swr_shuffle_correlation_histogram(
    infos,
    group_name,
    *,
    swr_correlations_shuffled,
    swr_shuffled_percentiles,
    savepath,
):
    for trajectory in meta.trajectories:
        _plot_swr_correlation_histogram(
            correlations=swr_correlations_shuffled[trajectory][:, 0],
            shuffled=swr_correlations_shuffled[trajectory][:, 1:],
            percentiles=swr_shuffled_percentiles[trajectory],
            color=meta.colors[trajectory],
            savepath=savepath[trajectory],
        )


def _plot_swr_correlation_histogram(
    correlations, shuffled, percentiles, color, title=None, savepath=None
):
    assert savepath is not None
    bins = np.linspace(-1, 1, 20)
    width = (bins[1] - bins[0]) * 0.4
    bin_centers = np.linspace(-1, 1, 19)

    fig, ax = plt.subplots(figsize=(8, 6))
    plt.bar(
        bin_centers + width / 2,
        np.histogram(correlations, bins=bins)[0],
        width=width,
        color=color,
        label="Single" if "shuffle" in savepath else "Data",
    )

    counts, _ = np.histogram(shuffled, bins=bins)
    plt.bar(
        bin_centers - width / 2,
        counts / meta.n_shuffles,
        width=width,
        color="k",
        label="Shuffled",
    )

    if percentiles is not None:
        with np.errstate(invalid="ignore"):
            replays = (percentiles <= meta.significant) | (
                percentiles >= 100 - meta.significant
            )
        plt.bar(
            bin_centers + width / 2,
            np.histogram(correlations[replays], bins=bins)[0],
            width=width,
            color="r",
            label=f"Significant\n"
            f"({len(correlations[replays])/len(correlations)*100:.2f} %)",
        )
    plt.locator_params(axis="y", nbins=6)
    plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    if title is not None:
        plt.title(title, fontsize=meta.fontsize)

    plt.legend(loc="best", fontsize=meta.fontsize_small)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(groups=meta_session.groups, savepath=("swrs", "swr_rate_bysubphase.svg"))
def plot_group_swr_rate_bysubphase(infos, group_name, *, swr_rate_bysubphase, savepath):
    fig, ax = plt.subplots(figsize=(8, 6))
    width = 0.8 / len(meta.subphases)

    heights = [[] for _ in meta.subphases]
    for i, subphase in enumerate(meta.subphases):
        means = np.array(
            [
                np.mean(swr_rate_bysubphase[phase][subphase]) * 60
                for phase in meta.run_times
            ]
        )
        sems = np.array(
            [
                scipy.stats.sem(np.array(swr_rate_bysubphase[phase][subphase]) * 60)
                for phase in meta.run_times
            ]
        )
        ax.bar(
            np.arange(len(meta.run_times)) + (i * width),
            means,
            width=width,
            color=meta.colors[subphase],
            yerr=sems,
            ecolor="k",
            label=meta.subphases_labels[subphase],
        )
        for i, (mean, sem) in enumerate(zip(means, sems)):
            heights[i].append(mean + sem)

    for left, right in [["start", "middle"], ["middle", "end"], ["start", "end"]]:
        for i, phase in enumerate(meta.run_times):
            height = max(
                heights[i][0 if left == "start" else 1],
                heights[i][1 if right == "middle" else 2],
            )
            if left == "start" and right == "end":
                height = max(heights[i]) * 1.07
            significance_bar(
                start=i + (0 if left == "start" else width),
                end=i + (width if right == "middle" else width * 2),
                height=height,
                pval=mannwhitneyu(
                    swr_rate_bysubphase[phase][left], swr_rate_bysubphase[phase][right]
                ),
            )
    if group_name in ["all", "combined", "day1", "r063"]:
        plt.legend(fontsize=meta.fontsize_small)

    if group_name not in ["all", "combined"]:
        plt.title(
            f"{meta.title_labels[group_name]}\nn = {len(infos)} sessions",
            fontsize=meta.fontsize,
        )
    plt.xticks(
        np.arange(len(meta.run_times)) + width,
        list(meta.run_times_labels.values()),
        fontsize=meta.fontsize,
    )
    plt.ylabel("SWR rate (events/min)", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    if group_name not in ["all", "combined"]:
        plt.ylim(0, 38)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(groups=meta_session.analysis_grouped, savepath=("swrs", "swr_rate_byday.svg"))
def plot_swr_rate_byday(infos, group_name, *, n_swrs_byday, swr_rate_byday, savepath):
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(8) + 1
    means = np.array([np.mean(val) for val in swr_rate_byday])
    sems = np.array([scipy.stats.sem(val) for val in swr_rate_byday])
    heights = means + sems
    rects = ax.bar(
        x,
        means,
        width=0.65,
        color=meta.colors["rest"],
        yerr=sems,
        ecolor="k",
    )

    # for n_swrs, rect in zip(n_swrs_byday, rects):
    #     ax.annotate(
    #         f"{np.sum(n_swrs)}",
    #         xy=(rect.get_x() + rect.get_width() / 2, 0),
    #         xytext=(0, 3),  # 3 points vertical offset
    #         textcoords="offset points",
    #         ha="center",
    #         va="bottom",
    #         fontsize=meta.fontsize_small,
    #     )

    # if n_phases == 7:
    #     used_heights = []
    #     tol = (plt.ylim()[1] - plt.ylim()[0]) * 0.06
    #     for left, right in zip(
    #         meta.rest_times[:-1] + meta.run_times[:-1],
    #         meta.rest_times[1:] + meta.run_times[1:],
    #     ):
    #         pval = mannwhitneyu(y_byphase[left], y_byphase[right])
    #         start = meta.task_times.index(left)
    #         end = meta.task_times.index(right)
    #         height = max(
    #             heights[start : end + 1].tolist() + [0],
    #         )
    #         while any(abs(height - used) < tol for used in used_heights):
    #             height += tol
    #         if pval < 0.05:
    #             significance_bar(
    #                 start=start,
    #                 end=end,
    #                 height=height,
    #                 pval=pval,
    #             )
    #             used_heights.append(height)

    # elif n_phases == 3:
    #     for left, right in [
    #         ("phase1", "phase2"),
    #         ("phase1", "phase3"),
    #         ("phase2", "phase3"),
    #     ]:
    #         pval = mannwhitneyu(y_byphase[left], y_byphase[right])
    #         start = meta.run_times.index(left)
    #         end = meta.run_times.index(right)
    #         significance_bar(
    #             start=start,
    #             end=end,
    #             height=max(
    #                 heights[start : end + 1].tolist() + [0],
    #             ),
    #             pval=pval,
    #         )

    plt.xticks(x, fontsize=meta.fontsize)
    plt.ylabel("Mean SWR rate (events / min)", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)
