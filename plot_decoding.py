import matplotlib.pyplot as plt
import nept
import numpy as np

import meta
import meta_session
from plots import (
    plot_aligned_position_and_spikes,
    plot_both_by_standard_position,
    plot_by_standard_position,
    significance_text,
)
from tasks import task


@task(groups=meta_session.groups, savepath=("decoding", "std_error.svg"))
def plot_error_boxplot(infos, group_name, *, decoding_error, savepath):
    fig, ax = plt.subplots(figsize=(7, 6))
    bp = ax.boxplot(
        [decoding_error["u"], decoding_error["full_shortcut"]],
        whis=(5, 95),
        patch_artist=True,
    )

    colors = [meta.colors["u"], meta.colors["full_shortcut"]]

    # change outline color, fill color and linewidth of the boxes
    for i, box in enumerate(bp["boxes"]):
        # change outline color
        box.set(color="#525252", linewidth=2)
        # change fill color
        box.set(facecolor=colors[i])

    # change color and linewidth of the whiskers
    for whisker in bp["whiskers"]:
        whisker.set(color="#525252", linewidth=2)

    # change color and linewidth of the caps
    for cap in bp["caps"]:
        cap.set(color="#525252", linewidth=2)

    # change color and linewidth of the medians
    for median in bp["medians"]:
        median.set(color="#525252", linewidth=2)

    # change the style of fliers and their fill
    for flier in bp["fliers"]:
        flier.set(marker=".", color="#bdbdbd", alpha=0.5, rasterized=True)

    ax.set_xticklabels(["Familiar", "Shortcut"], fontsize=meta.fontsize)
    ax.set_yticklabels(np.arange(-20, 101, 20), fontsize=meta.fontsize)
    ax.set_ylabel("Error (std unit)", fontsize=meta.fontsize)

    s = f"n = {len(infos)} sessions" if len(infos) > 1 else "Example session"
    plt.text(
        0.86,
        1.04,
        s=s,
        fontsize=meta.fontsize_small,
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
    )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)
    plt.savefig(savepath, bbox_inches="tight", transparent=True, dpi=meta.rasterize_dpi)
    plt.close(fig)


@task(infos=meta_session.all_infos, savepath=("decoding", "std_error_bybin.svg"))
def plot_mean_error_bybin(info, *, mean_error_bybin, savepath):
    if np.all(np.isnan(mean_error_bybin["u"])) or np.all(
        np.isnan(mean_error_bybin["full_shortcut"])
    ):
        print(f"No decoded positions for {info.session_id}?")
        return

    plot_both_by_standard_position(
        mean_error_bybin,
        ylabel="Mean decoding error (std unit)",
        savepath=savepath,
    )


@task(groups=meta_session.groups, savepath=("decoding", "std_error_bybin.svg"))
def plot_group_mean_error_bybin(infos, group_name, *, mean_error_bybin, savepath):
    plot_both_by_standard_position(
        mean_error_bybin,
        ylabel="Mean decoding error (std unit)",
        std_axvlines=True,
        ylim=15,
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in meta.trajectories
        },
        savepath=savepath,
    )


@task(groups=meta_session.groups, savepath=("decoding", "replay_decoding_bybin.svg"))
def plot_group_replay_decoding_bybin(
    infos, group_name, *, replay_decoding_bybin, savepath
):
    plot_both_by_standard_position(
        replay_decoding_bybin,
        std_axvlines=True,
        ylim=600,
        ylabel="Decoded counts during replays",
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in meta.trajectories
        },
        savepath=savepath,
    )


@task(
    infos=meta_session.analysis_infos,
    savepath=("decoding", "replay_likelihood_bybin.svg"),
)
def plot_replay_likelihood_bybin(info, *, replay_likelihood_bybin, savepath):
    plot_both_by_standard_position(
        replay_likelihood_bybin,
        std_axvlines=True,
        ylabel="Mean posterior during replays",
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in meta.trajectories
        },
        savepath=savepath,
    )


@task(groups=meta_session.groups, savepath=("decoding", "replay_likelihood_bybin.svg"))
def plot_group_replay_likelihood_bybin(
    infos, group_name, *, replay_likelihood_bybin, savepath
):
    plot_both_by_standard_position(
        replay_likelihood_bybin,
        std_axvlines=True,
        ylabel="Mean posterior during replays",
        ylim=0.03,
        title={
            trajectory: meta.trajectories_labels[trajectory]
            for trajectory in meta.trajectories
        },
        savepath=savepath,
    )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        task_time: ("decoding", f"replay_likelihood_bybin_{task_time}.svg")
        for task_time in meta.task_times
    },
)
def plot_replay_likelihood_bybin_byphase(
    info, *, replay_likelihood_bybin_byphase, savepath
):
    for i, task_time in enumerate(meta.task_times):
        plot_both_by_standard_position(
            replay_likelihood_bybin_byphase[task_time],
            std_axvlines=True,
            ylabel="Mean posterior during replays",
            suptitle=meta.task_times_labels[task_time],
            savepath=savepath[task_time],
        )


@task(
    groups=meta_session.groups,
    savepath={
        task_time: ("decoding", f"replay_likelihood_bybin_{task_time}.svg")
        for task_time in meta.task_times
    },
)
def plot_group_replay_likelihood_bybin_byphase(
    infos, group_name, *, replay_likelihood_bybin_byphase, savepath
):
    for i, task_time in enumerate(meta.task_times):
        plot_both_by_standard_position(
            replay_likelihood_bybin_byphase[task_time],
            std_axvlines=True,
            ylabel="Mean posterior during replays",
            ylim=0.041,
            suptitle=meta.task_times_labels[task_time],
            savepath=savepath[task_time],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        task_time: ("decoding", f"joined_replay_likelihood_bybin_{task_time}.svg")
        for task_time in meta.task_times
    },
)
def plot_joined_replay_likelihood_bybin_byphase(
    info, *, joined_replay_likelihood_bybin_byphase, savepath
):
    for i, task_time in enumerate(meta.task_times):
        plot_by_standard_position(
            joined_replay_likelihood_bybin_byphase[task_time],
            color=meta.colors["both"],
            ylabel="Mean posterior during replays",
            axvlines=[50],
            title="Familiar             Shortcut",
            std_xticks=False,
            savepath=savepath[task_time],
        )


@task(
    groups=meta_session.groups,
    savepath={
        task_time: ("decoding", f"joined_replay_likelihood_bybin_{task_time}.svg")
        for task_time in meta.task_times
    },
)
def plot_group_joined_replay_likelihood_bybin_byphase(
    infos, group_name, *, joined_replay_likelihood_bybin_byphase, savepath
):
    for i, task_time in enumerate(meta.task_times):
        plot_by_standard_position(
            joined_replay_likelihood_bybin_byphase[task_time],
            color=meta.colors["both"],
            ylabel="Mean posterior during replays",
            axvlines=[50],
            ylim=[0, 0.085],
            title=meta.task_times_labels[task_time] + "\nFamiliar             Shortcut",
            std_xticks=False,
            savepath=savepath[task_time],
        )


@task(
    groups=meta_session.groups,
    savepath=("decoding", "joined_replay_likelihood_bybin.svg"),
)
def plot_joined_replay_likelihood_bybin(
    infos, group_name, *, joined_replay_likelihood_bybin, savepath
):
    plot_by_standard_position(
        joined_replay_likelihood_bybin,
        ylabel="Mean posterior during replays",
        color="k",
        axvlines=[50],
        title="Familiar             Shortcut",
        std_xticks=False,
        savepath=savepath,
    )


@task(
    infos=meta_session.analysis_infos,
    savepath=("decoding", "replay_likelihood_bybin.svg"),
)
def plot_replay_likelihood_bybin(info, *, replay_likelihood_bybin, savepath):
    plot_both_by_standard_position(
        replay_likelihood_bybin,
        std_axvlines=True,
        ylabel="Mean posterior during replays",
        savepath=savepath,
    )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        f"{traj}-{i}": ("decoding", f"decoded_trial_{traj}-{i}.svg")
        for i in range(5)
        for traj in meta.trajectories
    },
)
def plot_decoded_trial(
    info,
    *,
    position,
    position_byzone,
    matched_linear,
    decoded,
    matched_tc_spikes,
    trials,
    savepath,
):

    for trajectory in meta.trajectories:
        run_epoch = nept.run_threshold(
            matched_linear[trajectory],
            thresh=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )

        t_starts = decoded[trajectory].time
        t_stops = t_starts + meta.decoding_dt
        decoding_epoch = nept.Epoch(t_starts, t_stops).merge()

        plot_aligned_position_and_spikes(
            position=position,
            position_traj=position_byzone[trajectory],
            linear=matched_linear[trajectory][run_epoch],
            linear_traj=decoded[trajectory],
            spikes=matched_tc_spikes[trajectory],
            spikes_traj=[
                spikes.time_slice(decoding_epoch.starts, decoding_epoch.stops)
                for spikes in matched_tc_spikes[trajectory]
            ],
            epochs=trials[trajectory],
            color=meta.colors[trajectory],
            n_epochs=5,
            savepath=[
                path for key, path in savepath.items() if key.startswith(trajectory)
            ],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        f"{i}": ("decoding", f"joined_decoded_replay-{i}.svg") for i in range(30)
    },
)
def plot_joined_decoded_replay(
    info,
    *,
    joined_decoded,
    joined_tc_spikes,
    joined_replays,
    savepath,
):
    t_starts = joined_decoded.time
    t_stops = t_starts + meta.decoding_dt
    decoding_epoch = nept.Epoch(t_starts, t_stops).merge()

    plot_aligned_position_and_spikes(
        position=None,
        position_traj=None,
        linear=None,
        linear_traj=joined_decoded,
        spikes=joined_tc_spikes,
        spikes_traj=[
            spikes.time_slice(decoding_epoch.starts, decoding_epoch.stops)
            for spikes in joined_tc_spikes
        ],
        epochs=joined_replays,
        color=meta.colors["joined"],
        n_epochs=30,
        t_buffer=meta.decoding_window,
        savepath=list(savepath.values()),
    )


def _plot_decoding_preference(
    preference,
    shuffled,
    ylabel,
    full_shuffle,
    axhline=None,
    ylim=None,
    title=None,
    figsize=(8, 6),
    savepath=None,
):
    assert savepath is not None
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(meta.task_times))
    mean_preference = [np.nanmean(preference[phase]) for phase in meta.task_times]
    pvals = []
    for i, phase in enumerate(meta.task_times):
        shuffle_means = np.nanmean(shuffled[phase], axis=0)
        np.sort(shuffle_means)
        rank = np.searchsorted(shuffle_means, mean_preference[i])
        rank /= shuffle_means.size
        pvals.append(2 * min(rank, 1 - rank))

    if axhline is not None:
        color = [
            meta.colors["full_shortcut"]
            if phase_preference > axhline
            else meta.colors["u"]
            for phase_preference in mean_preference
        ]
    else:
        color = ["k" for _ in mean_preference]
    plt.plot(mean_preference, color="k")
    for i, (phase_preference, phase_color) in enumerate(zip(mean_preference, color)):
        plt.scatter(x[i], phase_preference, color=phase_color, marker="o", s=200)

    plt.xticks(
        np.arange(len(meta.task_times)),
        list(meta.task_times_labels.values()),
        fontsize=meta.fontsize,
        rotation=meta.xtickrotation,
    )
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    if ylim is not None:
        plt.ylim(ylim)

    for i, phase_preference in enumerate(mean_preference):
        significance_text(x[i], phase_preference, pvals[i])

    plt.locator_params(axis="y", nbins=6)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    if axhline is not None:
        plt.axhline(axhline, c="k", ls="--")

    if title is not None:
        plt.title(title, fontsize=meta.fontsize)

    if not full_shuffle:
        plt.figtext(
            0.5,
            1.0,
            "Warning!! Plot not run with full shuffle!",
            fontsize=meta.fontsize,
            color="r",
            ha="center",
            va="baseline",
        )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath=("decoding", "zscored_logodds_byphase.svg"),
)
def plot_zscored_logodds_byphase(
    info, *, zscored_logodds, shuffled_zscored_logodds, savepath
):
    _plot_decoding_preference(
        zscored_logodds,
        shuffled=shuffled_zscored_logodds,
        ylabel="Z-scored log odds",
        full_shuffle=shuffled_zscored_logodds["prerecord"].size
        == meta.n_likelihood_shuffles,
        axhline=0.0,
        savepath=savepath,
    )


@task(
    groups=meta_session.groups,
    savepath=("decoding", "zscored_logodds_byphase.svg"),
)
def plot_group_zscored_logodds_byphase(
    infos, group_name, *, zscored_logodds, shuffled_zscored_logodds, savepath
):
    full_shuffle = shuffled_zscored_logodds[
        "prerecord"
    ].size == meta.n_likelihood_shuffles * len(infos)
    _plot_decoding_preference(
        zscored_logodds,
        shuffled=shuffled_zscored_logodds,
        ylabel="Z-scored log odds",
        full_shuffle=full_shuffle,
        axhline=0.0,
        ylim=(-1.5, 2.1) if group_name not in ["all", "combined"] else (-1.0, 1.0),
        title=meta.title_labels[group_name] + f"\n n = {len(infos)} sessions"
        if group_name not in ["all", "combined"]
        else None,
        figsize=(6, 6) if group_name in ["all", "combined"] else (8, 6),
        savepath=savepath,
    )


def _plot_logodds(logodds, ylabel, axhline=None, ylim=None, savepath=None):
    assert savepath is not None
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(meta.task_times))
    mean_preference = [np.nanmean(logodds[phase]) for phase in meta.task_times]
    if axhline is not None:
        color = [
            meta.colors["full_shortcut"]
            if phase_preference > axhline
            else meta.colors["u"]
            for phase_preference in mean_preference
        ]
    else:
        color = ["k" for _ in mean_preference]
    plt.plot(mean_preference, color="k")
    for i, (phase_preference, phase_color) in enumerate(zip(mean_preference, color)):
        plt.scatter(x[i], phase_preference, color=phase_color, marker="o")
    plt.xticks(np.arange(len(meta.task_times)), meta.task_times, fontsize=meta.fontsize)
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    if ylim is not None:
        plt.ylim(0, ylim)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    if axhline is not None:
        plt.axhline(axhline, c="k", ls="--")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    groups=meta_session.analysis_grouped,
    savepath=("decoding", "together_zscored_logodds_byphase.svg"),
)
def plot_together_zscored_logodds_byphase(
    infos,
    group_name,
    *,
    zscored_logodds,
    all_zscored_logodds,
    all_shuffled_zscored_logodds,
    savepath,
):
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(meta.task_times))
    axhline = 0.0

    for logodd in all_zscored_logodds:
        mean_preference = [np.nanmean(logodd[phase]) for phase in meta.task_times]
        color = [
            meta.colors["full_shortcut"]
            if phase_preference > axhline
            else meta.colors["u"]
            for phase_preference in mean_preference
        ]

        for i, (phase_preference, phase_color) in enumerate(
            zip(mean_preference, color)
        ):
            plt.scatter(x[i], phase_preference, color=phase_color, marker="o")

    mean_preference = [np.nanmean(zscored_logodds[phase]) for phase in meta.task_times]
    plt.plot(mean_preference, color="k")
    plt.scatter(x, mean_preference, color="k", marker="o")

    plt.xticks(np.arange(len(meta.task_times)), meta.task_times, fontsize=meta.fontsize)
    plt.ylabel("Z-scored log odds", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    if axhline is not None:
        plt.axhline(axhline, c="k", ls="--")

    if all_shuffled_zscored_logodds[0]["prerecord"].size != meta.n_likelihood_shuffles:
        plt.figtext(
            0.5,
            1.0,
            "Warning!! Plot not run with full shuffle!",
            fontsize=meta.fontsize,
            color="r",
            ha="center",
            va="baseline",
        )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)
