import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

import meta
import meta_session
from plots import significance_bar, significance_text
from tasks import task
from utils import mannwhitneyu


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays-session", f"{key}_replay_prop_byphase.svg")
        for key in [
            "exclusive",
            "exclusive_ph2",
            "difference",
            "difference_ph2",
        ]
    },
)
def plot_group_replay_prop_byphase(infos, group_name, *, replay_prop_byphase, savepath):
    _plot_replay_metric(
        replay_prop_byphase,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        savepath=savepath["exclusive"],
    )
    _plot_replay_metric(
        replay_prop_byphase,
        ["only_u_ph2", "only_full_shortcut_ph2"],
        ylabel="Proportion of SWRs\nthat are replays",
        savepath=savepath["exclusive_ph2"],
    )
    _plot_replay_metric(
        replay_prop_byphase,
        ["difference"],
        ylabel="Replay proportion\nfor shortcut - familiar",
        color_byvalue=True,
        savepath=savepath["difference"],
    )
    _plot_replay_metric(
        replay_prop_byphase,
        ["difference_ph2"],
        ylabel="Replay proportion\nfor shortcut - familiar",
        color_byvalue=True,
        savepath=savepath["difference_ph2"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        f"exclusive-{trajectory}": (
            "replays-session",
            f"exclusive_replay_prop_normalized_byphase_{trajectory}.svg",
        )
        for trajectory in meta.trajectories
    },
)
def plot_replay_prop_normalized_byphase(
    infos,
    group_name,
    *,
    replay_prop_normalized_byphase,
    savepath,
):
    for trajectory in meta.trajectories:
        _plot_replay_metric(
            replay_prop_normalized_byphase,
            [f"only_{trajectory}"],
            ylabel="Replay proportion /\nmean replay proportion",
            title=f"{meta.title_labels[group_name]}"
            if group_name not in ["all", "combined"]
            else None,
            savepath=savepath[f"exclusive-{trajectory}"],
        )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays-session", f"{key}_replay_prop_byexperience_bytrial.svg")
        for key in ["exclusive", "difference"]
    },
)
def plot_group_replay_prop_byexperience(
    infos,
    group_name,
    *,
    replay_prop_byexperience_bytrial,
    savepath,
):
    _plot_replay_metric(
        replay_prop_byexperience_bytrial,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of SWRs\nthat are replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )
    _plot_replay_metric(
        replay_prop_byexperience_bytrial,
        ["difference"],
        ylabel="Replay proportion\nfor shortcut - familiar",
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["difference"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("replays-session", f"{key}_replay_prop_byexperience_nofeeder_bytrial.svg")
        for key in ["exclusive", "difference"]
    },
)
def plot_group_replay_prop_byexperience_nofeeder_bytrial(
    infos,
    group_name,
    *,
    replay_prop_byexperience_nofeeder_bytrial,
    savepath,
):
    _plot_replay_metric(
        replay_prop_byexperience_nofeeder_bytrial,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of path SWRs\nthat are replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["exclusive"],
    )
    _plot_replay_metric(
        replay_prop_byexperience_nofeeder_bytrial,
        ["difference"],
        ylabel="Path replay proportion\nfor shortcut - familiar",
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        savepath=savepath["difference"],
    )


@task(
    groups=meta_session.groups,
    savepath={
        key: (
            "replays-session",
            f"{key}_replay_prop_byexperience_feederonly.svg",
        )
        for key in ["exclusive", "difference"]
    },
)
def plot_group_replay_prop_byexperience_feederonly(
    infos,
    group_name,
    *,
    replay_prop_byexperience_feederonly,
    savepath,
):
    original_xlabels = meta.on_task
    labels = meta.on_task_labels

    _plot_replay_metric(
        replay_prop_byexperience_feederonly,
        ["only_u", "only_full_shortcut"],
        ylabel="Proportion of feeder SWRs\nthat are replays",
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["exclusive"],
    )
    _plot_replay_metric(
        replay_prop_byexperience_feederonly,
        ["difference"],
        ylabel="Feeder replay proportion\nfor shortcut - familiar",
        color_byvalue=True,
        title=f"{meta.title_labels[group_name]}"
        if group_name not in ["all", "combined"]
        else None,
        original_xlabels=original_xlabels,
        labels=labels,
        savepath=savepath["difference"],
    )


def _plot_replay_metric(
    replay_metric,
    trajectories,
    ylabel,
    ylim=None,
    color_byvalue=False,
    title=None,
    original_xlabels=meta.experiences,
    labels=meta.experiences_labels,
    savepath=None,
):
    assert savepath is not None
    orig_xlabels = list(next(iter(replay_metric.values())))
    if orig_xlabels == meta.task_times:
        xlabels = list(meta.task_times_labels.values())
    else:
        assert orig_xlabels == original_xlabels, orig_xlabels
        xlabels = list(labels.values())
    x = np.arange(len(xlabels))
    width = 0.8 / (len(trajectories))
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot bars
    heights = {}
    for i, trajectory in enumerate(trajectories):
        if color_byvalue:
            color = [
                meta.colors["full_shortcut"] if np.mean(val) > 0.0 else meta.colors["u"]
                for val in list(replay_metric[trajectory].values())
            ]
        else:
            color = meta.colors[trajectory]
        means = np.array([np.mean(val) for val in replay_metric[trajectory].values()])
        sems = np.array(
            [scipy.stats.sem(val) for val in replay_metric[trajectory].values()]
        )
        plt.bar(
            x + i * width,
            means,
            yerr=sems,
            width=width,
            color=color,
            ecolor="k",
        )
        heights[trajectory] = means + sems

    if len(trajectories) == 2 and "full_shortcut" in trajectories[1]:
        pval = {
            xlabel: mannwhitneyu(
                replay_metric[trajectories[0]][xlabel],
                replay_metric[trajectories[1]][xlabel],
            )
            for xlabel in orig_xlabels
        }
        for i, xlabel in enumerate(orig_xlabels):
            significance_bar(
                start=i - 0.05,
                end=i + width + 0.05,
                height=max(
                    heights[trajectories[0]][i],
                    heights[trajectories[1]][i],
                    0,
                ),
                pval=pval[xlabel],
            )
    elif len(trajectories) == 1 and trajectories[0].startswith("difference"):
        prefix = "only_" if trajectories[0].startswith("difference") else ""
        suffix = "_ph2" if trajectories[0].endswith("_ph2") else ""
        pval = {
            xlabel: mannwhitneyu(
                replay_metric[f"{prefix}u{suffix}"][xlabel],
                replay_metric[f"{prefix}full_shortcut{suffix}"][xlabel],
            )
            for xlabel in orig_xlabels
        }

        for i, xlabel in enumerate(orig_xlabels):
            significance_text(
                x=i,
                height=max(heights[trajectories[0]][i], 0),
                pval=pval[xlabel],
            )
    else:
        # trajectories == ["u"] or ["full_shortcut"], for normalized plots
        for left, right in zip(
            meta.rest_times[:-1] + meta.run_times[:-1],
            meta.rest_times[1:] + meta.run_times[1:],
        ):
            pval = mannwhitneyu(
                replay_metric[trajectories[0]][left],
                replay_metric[trajectories[0]][right],
            )
            start = meta.task_times.index(left)
            end = meta.task_times.index(right)
            significance_bar(
                start=start,
                end=end,
                height=max(
                    list(heights[trajectories[0]])[start : end + 1] + [0],
                ),
                pval=pval,
            )

    offset = 0.0
    if len(trajectories) == 2:
        offset = 0.2
    elif len(trajectories) == 3:
        offset = 0.8 / 3
    plt.xticks(x + offset, xlabels, fontsize=meta.fontsize, rotation=meta.xtickrotation)
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    if "normalized" in savepath:
        plt.axhline(1.0, c="k", ls="--")
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.locator_params(axis="y", nbins=5)
    if ylim is not None:
        plt.ylim(0, ylim)
    if title is not None:
        plt.title(title, fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    groups=meta_session.analysis_grouped,
    savepath=("replays", "replay_participation_rate.svg"),
)
def plot_replay_participation_rate(
    infos, group_name, *, replay_participation_rate, savepath
):
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(3)
    means = np.array([np.mean(val) for val in replay_participation_rate.values()])
    sems = np.array(
        [scipy.stats.sem(val) for val in replay_participation_rate.values()]
    )
    heights = means + sems
    rects = ax.bar(
        x,
        means,
        width=0.65,
        color=meta.colors["rest"],
        yerr=sems,
        ecolor="k",
    )

    plt.xticks(x, ["Unique", "Non-unique", "No place field"], fontsize=meta.fontsize)
    plt.ylabel("Proportion of participating replays", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)
