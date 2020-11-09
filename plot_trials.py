import os

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import nept
import numpy as np
import scipy.stats
from scipy.ndimage import median_filter
from shapely.geometry import Point

import meta
import meta_session
import paths
from plots import plot_aligned_position_and_spikes
from tasks import task


def _plot_trial_proportions(infos, group_name, trial_proportions, ylabel, savepath):
    x = np.arange(len(trial_proportions))
    y = [np.mean(trial_proportions[trajectory]) for trajectory in meta.trial_types]
    sem = [
        scipy.stats.sem(trial_proportions[trajectory])
        for trajectory in meta.trial_types
    ]
    colors = [meta.colors[trajectory] for trajectory in meta.trial_types]
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.bar(x, y, color=colors, yerr=sem, ecolor="k")
    plt.xticks(
        x,
        [meta.trajectories_labels[trajectory] for trajectory in meta.trial_types],
        fontsize=meta.fontsize,
    )
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.ylim(0, 1.05)

    n_sessions = len(infos)
    if n_sessions == 1:
        txt = "Example session"
    else:
        txt = f"n = {n_sessions} sessions"

    title = (
        f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None
    )
    if title is not None:
        plt.title(title + f"\n{txt}", fontsize=meta.fontsize)
    else:
        plt.text(
            0.8,
            0.95,
            s=txt,
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=meta.fontsize_small,
        )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(groups=meta_session.groups, savepath=("behavior", "behavior_choice.svg"))
def plot_trial_proportions(infos, group_name, *, trial_proportions, savepath):
    _plot_trial_proportions(
        infos,
        group_name,
        trial_proportions,
        ylabel="Proportion of trials chosen",
        savepath=savepath,
    )


@task(
    groups=meta_session.groups, savepath=("behavior", "behavior_choice_firsttrial.svg")
)
def plot_firsttrial_proportions(
    infos, group_name, *, trial_proportions_bytrial, savepath
):
    firsttrial_proportions = {
        trajectory: trial_proportions_bytrial[trajectory][0]
        for trajectory in meta.trial_types
    }
    _plot_trial_proportions(
        infos,
        group_name,
        firsttrial_proportions,
        ylabel="Proportion of first trial chosen",
        savepath=savepath,
    )


@task(groups=meta_session.groups, savepath=("behavior", "behavior_duration.svg"))
def plot_trial_durations(infos, group_name, *, trial_durations, savepath):
    _plot_boxplot(
        y=[
            trial_durations["phase3"]["u"],
            trial_durations["phase3"]["full_shortcut"],
            trial_durations["phase3"]["novel"],
        ],
        n_sessions=len(infos),
        ylabel="Trial duration (s)",
        savepath=savepath,
    )


@task(groups=meta_session.groups, savepath=("behavior", "behavior_firsttrial.svg"))
def plot_behavior_firsttrial(infos, group_name, *, all_trial_durations, savepath):
    y = []
    for trajectory in meta.behavioral_trajectories:
        y.append([])
        for trial_durations in all_trial_durations:
            durations = trial_durations["phase3"][trajectory]
            if len(durations) > 0:
                y[-1].append(durations[0])

    _plot_boxplot(
        y=y,
        n_sessions=len(infos),
        ylabel="First trial durations (s)",
        savepath=savepath,
    )


def _plot_boxplot(y, n_sessions, ylabel, savepath):
    fig, ax = plt.subplots(figsize=(8, 6))

    box = plt.boxplot(
        y,
        patch_artist=True,
    )

    for patch, color in zip(
        box["boxes"],
        [meta.colors[trajectory] for trajectory in meta.behavioral_trajectories],
    ):
        patch.set(color="#252525", linewidth=2)
        patch.set(facecolor=color)
    for whisker in box["whiskers"]:
        whisker.set(color="#252525", linewidth=2)
    for cap in box["caps"]:
        cap.set(color="#252525", linewidth=2)
    for median in box["medians"]:
        median.set(color="#252525", linewidth=2)
    for flier in box["fliers"]:
        flier.set(marker=".", color="#252525", alpha=0.2)

    plt.ylabel(ylabel, fontsize=meta.fontsize)
    plt.xticks(
        [1, 2, 3],
        [
            meta.trajectories_labels[trajectory]
            for trajectory in meta.behavioral_trajectories
        ],
        fontsize=meta.fontsize,
    )
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    if n_sessions == 1:
        txt = "Example session"
    else:
        txt = f"n = {n_sessions} sessions"
    plt.text(
        0.8,
        1.05,
        s=txt,
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
        fontsize=meta.fontsize_small,
    )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    # TODO: set ylim?
    # plt.ylim(0, 100)

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


def _plot_behavior_bytrial(
    trial_proportions_bytrial,
    n_sessions,
    n_trials=None,
    title=None,
    legend_loc=None,
    show_legend=False,
    axvline=None,
    savepath=None,
):
    assert savepath is not None
    fig, ax = plt.subplots(figsize=(8, 6))

    trial_n = (
        np.arange(len([t for t in trial_proportions_bytrial["u"] if len(t) > 1])) + 1
    )
    if n_trials is not None:
        trial_n = trial_n[:n_trials]

    labels = [meta.trajectories_labels[trajectory] for trajectory in meta.trial_types]
    for i, trajectory in enumerate(meta.trial_types):
        this_proportions = trial_proportions_bytrial[trajectory]
        mean = median_filter(
            [np.mean(trial) for trial in this_proportions if len(trial) > 1],
            size=(3,),
            mode="nearest",
        )
        sem = median_filter(
            [scipy.stats.sem(trial) for trial in this_proportions if len(trial) > 1],
            size=(3,),
            mode="nearest",
        )
        if n_trials is not None:
            mean = mean[:n_trials]
            sem = sem[:n_trials]

        plt.plot(
            trial_n,
            mean,
            color=meta.colors[trajectory],
            marker="o",
            lw=2,
            label=labels[i],
        )
        ax.fill_between(
            trial_n,
            mean - sem,
            mean + sem,
            color=meta.colors[trajectory],
            interpolate=True,
            alpha=0.3,
        )

    plt.ylabel("Proportion of trials", fontsize=meta.fontsize)
    plt.xlabel("Trial", fontsize=meta.fontsize)
    plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if n_trials == 80:
        plt.xticks([1, 10, 20, 30, 40, 50, 60, 70, 80])
    else:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, prune="lower"))

    plt.ylim(0, 1.05)

    if n_sessions == 1:
        txt = "Example session"
    else:
        txt = f"n = {n_sessions} sessions"

    if title is not None:
        plt.title(title + f"\n{txt}", fontsize=meta.fontsize)
    else:
        plt.text(
            0.8,
            1.05,
            s=txt,
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=meta.fontsize_small,
        )

    if axvline is not None:
        ax.axvline(axvline, linestyle="dashed", color="k")

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    if show_legend:
        ax.legend(
            loc=legend_loc if legend_loc is not None else "best",
            fontsize=meta.fontsize_small,
        )

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    groups=meta_session.groups,
    savepath={
        "all": ("behavior", "behavior_bytrial_all.svg"),
        "first_n": ("behavior", "behavior_bytrial_first_n.svg"),
        "first_consecutive": ("behavior", "behavior_bytrial_first_consecutive.svg"),
    },
)
def plot_behavior_bytrial(infos, group_name, *, trial_proportions_bytrial, savepath):
    _plot_behavior_bytrial(
        trial_proportions_bytrial,
        len(infos),
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        legend_loc="upper left"
        if group_name in ["all", "combined", "r063", "day1"]
        else "best",
        show_legend=True
        if group_name in ["all", "combined", "r063", "day1"]
        else False,
        savepath=savepath["all"],
    )
    _plot_behavior_bytrial(
        trial_proportions_bytrial,
        len(infos),
        n_trials=meta.first_n_trials,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        legend_loc="upper left"
        if group_name in ["all", "combined", "r063", "day1"]
        else "best",
        show_legend=True
        if group_name in ["all", "combined", "r063", "day1"]
        else False,
        savepath=savepath["first_n"],
    )


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "behavior_bytrial_consecutive.svg"),
)
def plot_behavior_bytrial_consecutive(
    infos, group_name, *, trial_proportions_bytrial, mostly_shortcut_idx, savepath
):
    _plot_behavior_bytrial(
        trial_proportions_bytrial,
        len(infos),
        n_trials=meta.first_n_trials_consecutive,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        legend_loc="center right"
        if group_name in ["all", "combined", "r063", "day1"]
        else "best",
        show_legend=True
        if group_name in ["all", "combined", "r063", "day1"]
        else False,
        axvline=mostly_shortcut_idx + 1,
        savepath=savepath,
    )


@task(infos=meta_session.analysis_infos)
def plot_raw_trials(
    info,
    *,
    position,
    raw_position_byzone,
    raw_trials,
    lines,
):
    n_trials = raw_trials.n_epochs
    savepath = [
        paths.plot_file(f"ind-{info.session_id}", "ind-raw-trials", f"trial-{i}.svg")
        for i in range(n_trials)
    ]
    os.makedirs(os.path.dirname(savepath[0]), exist_ok=True)

    plot_aligned_position_and_spikes(
        position=position,
        position_traj=raw_position_byzone["u"],
        position_xlim=(info.xedges[0], info.xedges[-1]),
        position_ylim=(info.yedges[0], info.yedges[-1]),
        linear=nept.Position(position.x, position.time),
        linear_traj=nept.Position(position.y, position.time),
        spikes=None,
        spikes_traj=None,
        linear_ylim=(np.min(position.data), np.max(position.data)),
        epochs=raw_trials,
        color=meta.colors["u"],
        matched_ends=(
            Point(*info.path_pts["feeder1"]),
            Point(*info.path_pts["feeder2"]),
        ),
        n_epochs=n_trials,
        savepath=savepath,
    )


@task(infos=meta_session.all_infos)
def plot_trials(
    info,
    *,
    position,
    position_byzone,
    trials,
    lines,
):
    for trial_type in meta.trial_types:
        n_trials = trials[trial_type].n_epochs
        if n_trials == 0:
            continue

        savepath = [
            paths.plot_file(
                f"ind-{info.session_id}", "ind-trials", f"trial-{trial_type}-{i}.svg"
            )
            for i in range(n_trials)
        ]
        os.makedirs(os.path.dirname(savepath[0]), exist_ok=True)

        plot_aligned_position_and_spikes(
            position=position,
            position_traj=position_byzone["u"]
            if trial_type == "exploratory"
            else position_byzone[trial_type],
            position_xlim=(info.xedges[0], info.xedges[-1]),
            position_ylim=(info.yedges[0], info.yedges[-1]),
            linear=nept.Position(position.x, position.time),
            linear_traj=nept.Position(position.y, position.time),
            spikes=None,
            spikes_traj=None,
            linear_ylim=(np.min(position.data), np.max(position.data)),
            epochs=trials[trial_type],
            color=meta.colors[trial_type],
            matched_ends=(
                Point(*info.path_pts["feeder1"]),
                Point(*info.path_pts["feeder2"]),
            ),
            n_epochs=n_trials,
            savepath=savepath,
        )


@task(infos=meta_session.all_infos, savepath=("mazes", "maze_first_trials.svg"))
def plot_first_trials(info, *, position, task_times, trials, savepath):
    fig, ax = plt.subplots(figsize=(8, 6))

    maze_times = nept.Epoch([], [])
    for run_time in meta.run_times:
        maze_times = maze_times.join(task_times[run_time])
    maze_position = position[maze_times]
    plt.plot(
        maze_position.x,
        maze_position.y,
        ".",
        color=meta.colors["rest"],
        ms=1.0,
        rasterized=True,
    )

    for trajectory in reversed(meta.behavioral_trajectories):
        if trials[trajectory].n_epochs > 0:
            plt.plot(
                maze_position[trials[trajectory][0]].x,
                maze_position[trials[trajectory][0]].y,
                ".",
                color=meta.colors[trajectory],
                ms=10.0,
            )

    plt.axis("off")
    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True, dpi=meta.rasterize_dpi)
    plt.close(fig)
