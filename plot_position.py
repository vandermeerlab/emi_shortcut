import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import statsmodels.api as sm

import meta
import meta_session
from plots import plot_bar_mean_byphase, plot_position, significance_bar
from tasks import task
from utils import latex_float


@task(
    groups=meta_session.groups,
    savepath={
        "full": ("pos", "speed_byphase_full.svg"),
        "rest": ("pos", "speed_byphase_rest.svg"),
    },
)
def plot_speed_byphase(
    infos,
    group_name,
    *,
    speed_byphase,
    speed_byphase_restonly,
    savepath,
):
    plot_bar_mean_byphase(
        speed_byphase, ylabel="Mean speed (bins / s)", savepath=savepath["full"]
    )
    plot_bar_mean_byphase(
        speed_byphase_restonly,
        ylabel="Mean speed (bins / s)",
        savepath=savepath["rest"],
    )


@task(groups=meta_session.groups, savepath=("behavior", "behavior_barriers.svg"))
def plot_behavior_bybarriers(infos, group_name, *, barrier_time, savepath):
    x = np.arange(2)
    width = 0.75
    y = [np.mean(barrier_time["shortcut"]), np.mean(barrier_time["novel"])]
    sem = [
        scipy.stats.sem(barrier_time["shortcut"]),
        scipy.stats.sem(barrier_time["novel"]),
    ]
    t, pval, df = sm.stats.ttest_ind(barrier_time["shortcut"], barrier_time["novel"])

    colors = [meta.colors["full_shortcut"], meta.colors["novel"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.bar(x, y, width=width, color=colors, yerr=sem, ecolor="k")
    significance_bar(x[0], x[1], max(y) + max(sem), pval)
    plt.xticks(x, ("Shortcut barrier", "Dead-end barrier"), fontsize=meta.fontsize)
    plt.ylabel("Mean time spent (s)", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.axhline(np.mean(barrier_time["baseline"]), -1, 2, linestyle="dashed", color="k")
    plt.xlim(-0.7, 1.7)
    plt.ylim(0, 115)
    n_sessions = len(barrier_time["shortcut"])

    title = (
        f"{meta.title_labels[group_name]} Phase 2\nn = {n_sessions} sessions"
        if group_name not in ["all", "combined"]
        else f"Phase 2\nn = {n_sessions} sessions"
    )
    plt.title(title, fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    infos=meta_session.all_infos,
    savepath={
        trajectory: ("mazes", f"maze-{trajectory}.svg")
        for trajectory in meta.trajectories
    },
)
def plot_sub_maze(info, *, position_byzone, savepath):
    for trajectory in meta.trajectories:
        plot_position(
            position_byzone[trajectory], meta.colors[trajectory], savepath[trajectory]
        )


@task(
    infos=meta_session.all_infos,
    savepath={
        task_time: ("mazes", f"maze-pos-{task_time}.svg")
        for task_time in meta.task_times
    },
)
def plot_task_time_positions(info, *, lines, task_times, position, savepath):
    n_positions = 10
    for task_time in meta.task_times:
        fig = plt.figure(figsize=(6, 6))
        for trajectory, line in lines.items():
            if trajectory.endswith("_with_feeders"):
                continue
            x, y = line.xy
            plt.plot(x, y, c=meta.colors[trajectory])

        start = task_times[task_time].start
        pos = position[position.time >= start][:n_positions]
        plt.plot(pos.x, pos.y, "o", c="k")
        start_diff = pos.time[0] - start

        stop = task_times[task_time].stop
        pos = position[position.time <= stop][-n_positions:]
        plt.plot(pos.x, pos.y, "o", c="r")
        stop_diff = stop - pos.time[-1]

        plt.title(
            f"{task_time}: {start:.0f}+{start_diff:.3f} to {stop:.0f}-{stop_diff:.3f}"
        )

        plt.tight_layout()

        plt.savefig(savepath[task_time], bbox_inches="tight", transparent=True)
        plt.close(fig)


@task(groups=meta_session.groups, savepath=("behavior", "barrier_scatter.svg"))
def plot_barrier_scatter(
    infos, group_name, *, barrier_t, barrier_dist_to_feeder, savepath
):
    fig, ax = plt.subplots(figsize=(8, 6))
    for barrier in meta.barriers:
        plt.scatter(
            barrier_dist_to_feeder[barrier],
            barrier_t[barrier],
            c=meta.colors[barrier],
            label=meta.barrier_labels[barrier],
        )

    def regress(x, y, c, height):
        slope, intercept, rval, pval, _ = scipy.stats.linregress(x, y)
        plt.plot(x, intercept + slope * x, c)
        plt.text(
            0.8,
            height,
            s=f"$r^2 = {rval ** 2:.3f}$\n$p = {latex_float(pval)}$",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=meta.fontsize_small,
            color=c,
        )

    x = np.hstack(list(barrier_dist_to_feeder.values()))
    y = np.hstack(list(barrier_t.values()))
    regress(x, y, "k", 0.9)
    regress(x[x > 0], y[x > 0], "r", 0.75)

    if group_name not in ["all", "combined"]:
        plt.title(meta.title_labels[group_name], fontsize=meta.fontsize)
    plt.xlabel("Distance to nearest feeder (cm)", fontsize=meta.fontsize)
    plt.ylabel("Time spent near barrier (s)", fontsize=meta.fontsize)
    plt.legend(loc="upper center", fontsize=meta.fontsize_small)

    plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout()

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)
