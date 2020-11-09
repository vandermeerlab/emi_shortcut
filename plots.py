import matplotlib.pyplot as plt
import numpy as np
import scalebar
import scipy.stats
from matplotlib.markers import TICKDOWN

import meta
from utils import map_range


def significance_text(x, height, pval):
    if pval < 0.001:
        text = "***"
    elif pval < 0.01:
        text = "**"
    elif pval < 0.05:
        text = "*"
    else:
        return False

    # draw the text with a bounding box covering up the line
    h_adjust = (plt.ylim()[1] - plt.ylim()[0]) * 0.01
    plt.text(
        x,
        height - h_adjust,
        text,
        ha="center",
        va="center",
        bbox=dict(facecolor="1.", edgecolor="none", boxstyle="Square,pad=0.1"),
        size=meta.fontsize - 6,
    )
    return True


def significance_bar(start, end, height, pval):
    if significance_text((start + end) * 0.5, height, pval):
        # draw a line with downticks at the ends
        linewidth = 1.2
        plt.plot(
            [start, end],
            [height, height],
            "-",
            color="k",
            lw=linewidth,
            marker=TICKDOWN,
            markeredgewidth=linewidth,
            markersize=8,
        )


def plot_raster(
    spikes,
    xlim,
    position=None,
    lfp=None,
    buffer=None,
    tuning_curves=None,
    correlation=None,
    correlation_p=None,
    percentile=None,
    swr_raster=None,
    swr_lfp=None,
    swr_buffer=None,
    savepath=None,
):
    size_lfp = 8
    if lfp is not None or position is not None or swr_lfp is not None:
        n_rows = len(spikes) + size_lfp
    else:
        n_rows = len(spikes)
    if tuning_curves is not None or position is not None:
        n_cols = 5
        raster_col = 2
    else:
        n_cols = 3
        raster_col = 0
    if swr_raster is not None or swr_lfp is not None:
        n_cols = 7
        raster_col = 2

    fig = plt.figure(figsize=(8, 6))
    gs = fig.add_gridspec(n_rows, n_cols)

    ax_raster = fig.add_subplot(gs[: len(spikes), raster_col : raster_col + 3])
    ax_raster.axis("off")
    ax_raster.eventplot(
        [spike.time for spike in spikes],
        colors=["k"],
        linelengths=0.8,
        linewidths=1,
    )
    ax_raster.set_ylim(len(spikes) - 0.5, -0.5)

    if correlation is not None and correlation_p is not None:
        correlation_text = (
            f"Correlation: {correlation:.3f}, p-value: {correlation_p:.3f}"
        )
        if percentile is not None:
            correlation_text += f", percentile: {percentile:.0f}"
        ax_raster.text(
            0.5,
            1.01,
            correlation_text,
            size=12,
            ha="center",
            va="bottom",
            transform=ax_raster.transAxes,
        )

    if lfp is None:
        if swr_raster is not None and swr_lfp is not None:
            scalebar_loc = (0.66, 0.2)
        elif swr_raster is not None:
            scalebar_loc = (0.66, 0.08)
        else:
            scalebar_loc = (0.9, 0.08)
        scalebar.add_scalebar(
            ax_raster,
            matchy=False,
            bbox_transform=fig.transFigure,
            bbox_to_anchor=scalebar_loc,
            units="s",
        )

    if position is not None:
        position_idx = len(spikes) + 1
        ax = fig.add_subplot(gs[position_idx : position_idx + size_lfp, 0])
        ax.plot(
            position.x, position.y, ".", color="#bdbdbd", alpha=0.2, rasterized=True
        )
        sliced_position = position.time_slice(xlim[0], xlim[1])
        ax.plot(sliced_position.x, sliced_position.y, "r.", ms=1)
        ax.axis("off")

    if lfp is not None:
        lfp_location = len(spikes) + 1
        ax = fig.add_subplot(
            gs[lfp_location : lfp_location + size_lfp, raster_col : raster_col + 3]
        )
        ax.plot(lfp.time, lfp.data, "k", lw=1)
        ax.axis("off")

        if buffer is not None:
            swr_lfp = lfp.time_slice(lfp.time[0] + buffer, lfp.time[-1] - buffer)
            ax.plot(swr_lfp.time, swr_lfp.data, "r", lw=1)

        scalebar_loc = (0.9, 0.1)
        scalebar.add_scalebar(
            ax,
            matchy=False,
            bbox_transform=fig.transFigure,
            bbox_to_anchor=scalebar_loc,
            units="ms",
        )

    if swr_raster is not None:
        swr_col = 5
        ax_swrraster = fig.add_subplot(gs[: len(swr_raster), swr_col:])
        ax_swrraster.axis("off")
        ax_swrraster.eventplot(
            [spikes.time for spikes in swr_raster],
            colors=["k"],
            linelengths=0.8,
            linewidths=1,
        )
        ax_swrraster.set_ylim(len(swr_raster) - 0.5, -0.5)

    if swr_lfp is not None and swr_raster is not None:
        lfp_location = len(spikes) + 1
        ax_swrlfp = fig.add_subplot(
            gs[lfp_location : lfp_location + size_lfp, swr_col : swr_col + 3]
        )
        ax_swrlfp.plot(swr_lfp.time, swr_lfp.data, "#3288bd", lw=1, color="#525252")
        ax_swrlfp.axis("off")

        if swr_buffer is not None:
            swr_lfp_only = swr_lfp.time_slice(
                swr_lfp.time[0] + swr_buffer, swr_lfp.time[-1] - swr_buffer
            )
            ax_swrlfp.plot(swr_lfp_only.time, swr_lfp_only.data, "b", lw=1)

        scalebar.add_scalebar(
            ax_swrlfp,
            matchy=False,
            bbox_transform=fig.transFigure,
            bbox_to_anchor=(0.9, 0.08),
            units="ms",
        )

    if tuning_curves is not None:
        assert len(tuning_curves) == len(spikes)
        ax_tcs = fig.add_subplot(gs[: len(tuning_curves), :raster_col])
        ax_tcs.axis("off")
        for i, tc in enumerate(reversed(tuning_curves)):
            ax_tcs.plot(map_range(tc, 0, np.max(tc), i, i + 0.96), color="k")
        ax_tcs.set_ylim(0, len(tuning_curves))

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


def plot_bar_mean_byphase(y_byphase, ylabel, n_byphase=None, savepath=None):
    n_phases = len(meta.task_times)
    x = np.arange(n_phases)

    fig, ax = plt.subplots(figsize=(8, 6))
    rects = ax.bar(
        x,
        [np.mean(y_byphase[phase]) for phase in meta.task_times],
        width=0.65,
        color=[
            meta.colors["rest"] if i % 2 == 0 else meta.colors["run"]
            for i in range(n_phases)
        ],
        yerr=[scipy.stats.sem(y_byphase[phase]) for phase in meta.task_times],
        ecolor="k",
    )

    if n_byphase is not None:
        for phase, rect in zip(meta.task_times, rects):
            ax.annotate(
                f"{np.sum(n_byphase[phase])}",
                xy=(rect.get_x() + rect.get_width() / 2, 0),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=meta.fontsize_small,
            )

    plt.xticks(
        x,
        list(meta.task_times_labels.values()),
        fontsize=meta.fontsize,
        rotation=meta.xtickrotation,
    )
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


def plot_position(position, color=meta.colors["u"], savepath=None):
    fig, axs = plt.subplots(position.dimensions, figsize=(8, 6))

    if not isinstance(axs, np.ndarray):
        axs = [axs]

    for i, ax in enumerate(axs):
        ax.plot(
            position.time,
            position.data[:, i],
            ".",
            color=color,
            rasterized=True,
        )

        ax.tick_params(labelsize=meta.fontsize)
        if i + 1 < len(axs):
            ax.set_xticks([])
        else:
            ax.set_xlabel("Time (s)", fontsize=meta.fontsize)
        ax.set_ylabel("Position (std units)", fontsize=meta.fontsize)

        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")
    plt.tight_layout()

    plt.savefig(savepath, bbox_inches="tight", transparent=True, dpi=meta.rasterize_dpi)
    plt.close(fig)


def plot_both_by_standard_position(
    value_bybin,
    ylabel,
    left="u",
    right="full_shortcut",
    std_axvlines=False,
    ylim=None,
    metric=None,
    ymetric=None,
    title=None,
    suptitle=None,
    savepath=None,
):
    if metric is None:
        metric = {left: None, right: None}
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 6))
    if ylim is None:
        ylim = np.nanmax([np.nanmax(value_bybin[left]), np.nanmax(value_bybin[right])])
    if suptitle is not None:
        fig.suptitle(suptitle, fontsize=meta.fontsize)

    if not np.all(np.isnan(value_bybin[left])):
        plot_by_standard_position(
            value_bybin[left],
            ylabel=ylabel,
            color=meta.colors[left],
            label="Familiar",
            axvlines=None if not std_axvlines else meta.std_axvlines[left],
            metric=metric[left],
            ymetric=None,
            ylim=(0, ylim),
            ax=ax1,
            title=title[left] if title is not None else None,
            savepath=None,
        )
    if not np.all(np.isnan(value_bybin[right])):
        plot_by_standard_position(
            value_bybin[right],
            ylabel=None,
            color=meta.colors[right],
            label="Shortcut",
            axvlines=None if not std_axvlines else meta.std_axvlines[right],
            metric=metric[right],
            ymetric=ymetric,
            ylim=(0, ylim),
            ax=ax2,
            title=title[right] if title is not None else None,
            savepath=None,
        )

    # fig.legend(loc="best", fontsize=meta.fontsize_small)

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


def plot_by_standard_position(
    value_bybin,
    ylabel,
    color,
    label=None,
    axvlines=None,
    metric=None,
    ymetric=None,
    ylim=None,
    ax=None,
    title=None,
    std_xticks=True,
    savepath=None,
):
    if ax is None:
        assert savepath is not None
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))

    ax.plot(
        meta.linear_bin_centers,
        value_bybin,
        "o",
        color=color,
        label=label,
    )
    axvlines = [] if axvlines is None else axvlines
    for axvline in axvlines:
        ax.axvline(axvline, linestyle="dashed", color="k")
    ax.tick_params(axis="both", which="major", labelsize=meta.fontsize)
    ax.set_xlabel("Linearized position bins", fontsize=meta.fontsize)
    if std_xticks:
        ax.set_xticks(meta.ticks)
    plt.locator_params(axis="y", nbins=6)
    if ylabel is not None:
        ax.set_ylabel(ylabel, fontsize=meta.fontsize)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    if metric is not None:
        ax_metric = ax.twinx()
        ax_metric.plot(
            meta.linear_bin_centers,
            metric,
            color="k",
        )
        if ymetric is not None:
            ax_metric.set_ylabel(ymetric, fontsize=meta.fontsize)

    if ylim is not None:
        ax.set_ylim(ylim)

    if title is not None:
        ax.set_title(title, fontsize=meta.fontsize)

    if savepath is not None:
        plt.tight_layout(h_pad=0.003)

        plt.savefig(savepath, bbox_inches="tight", transparent=True)
        plt.close(fig)


def plot_aligned_position_and_spikes(
    *,
    position,
    position_traj,
    linear,
    linear_traj,
    spikes,
    spikes_traj,
    epochs,
    color,
    position_xlim=None,
    position_ylim=None,
    linear_ylim=None,
    n_epochs=3,
    t_buffer=1.0,
    matched_ends=None,
    savepath=None,
):
    for i, epoch in enumerate(epochs[:n_epochs]):
        fig = plt.figure(figsize=(20, 6))
        gs = fig.add_gridspec(nrows=2, ncols=2)
        expanded_epoch = epoch.expand(t_buffer)

        # ax_pos
        ax_pos = fig.add_subplot(gs[:, 0])

        if position is not None:
            this_pos = position[epoch]
            ax_pos.plot(this_pos.x, this_pos.y, ".", color="k")

        if position_traj is not None:
            this_pos_traj = position_traj[epoch]
            ax_pos.plot(this_pos_traj.x, this_pos_traj.y, ".", color=color)

        if matched_ends is not None:
            ax_pos.plot(matched_ends[0].x, matched_ends[0].y, "ro")
            ax_pos.plot(matched_ends[1].x, matched_ends[1].y, "ro")

        if position_xlim is not None:
            ax_pos.set_xlim(position_xlim)
        if position_ylim is not None:
            ax_pos.set_ylim(position_ylim)

        # ax_linear
        ax_linear = fig.add_subplot(gs[0, 1])

        if linear is not None:
            this_linear = linear[expanded_epoch]
            ax_linear.plot(this_linear.time - epoch.start, this_linear.x, "k.")

        if linear_traj is not None:
            this_linear_traj = linear_traj[expanded_epoch]
            ax_linear.plot(
                this_linear_traj.time - epoch.start,
                this_linear_traj.x,
                ".",
                color=color,
            )
        ax_linear.axvline(0, c=color)
        ax_linear.axvline(epoch.durations[0], c=color)
        if "joined" in savepath[i]:
            ax_linear.axhline(50, c="k", ls="--")
        ax_linear.set_xlim(-t_buffer, epoch.durations[0] + t_buffer)
        if linear_ylim is None:
            ax_linear.set_ylim(meta.linear_bin_edges[0], meta.linear_bin_edges[-1])
        else:
            ax_linear.set_ylim(linear_ylim)

        # ax_spikes
        ax_spikes = fig.add_subplot(gs[1, 1])
        eventplot = {"linelengths": 0.8, "linewidths": 1}

        if spikes is not None:
            this_spikes = [
                spiketrain.time_slice(expanded_epoch.start, expanded_epoch.stop)
                for spiketrain in spikes
            ]
            ax_spikes.eventplot(
                [spiketrain.time - epoch.start for spiketrain in this_spikes],
                colors=["k"],
                **eventplot,
            )

        if spikes_traj is not None:
            this_spikes_traj = [
                spiketrain.time_slice(expanded_epoch.start, expanded_epoch.stop)
                for spiketrain in spikes_traj
            ]
            ax_spikes.eventplot(
                [spiketrain.time - epoch.start for spiketrain in this_spikes_traj],
                colors=[color],
                **eventplot,
            )
        ax_spikes.axvline(0, c=color)
        ax_spikes.axvline(epoch.durations[0], c=color)
        ax_spikes.set_xlim(-t_buffer, epoch.durations[0] + t_buffer)

        plt.tight_layout()

        plt.savefig(savepath[i], bbox_inches="tight", transparent=True)
        plt.close(fig)


def plot_replay_metric(
    replay_metric,
    trajectories,
    ylabel,
    pval=None,
    ylim=None,
    color_byvalue=False,
    title=None,
    savepath=None,
):
    assert savepath is not None
    orig_xlabels = list(next(iter(replay_metric.values())))
    if orig_xlabels == meta.task_times:
        xlabels = list(meta.task_times_labels.values())
    else:
        assert orig_xlabels == meta.experiences, orig_xlabels
        xlabels = list(meta.experiences_labels.values())
    x = np.arange(len(xlabels))
    width = 0.8 / (len(trajectories))
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot bars
    for i, trajectory in enumerate(trajectories):
        if color_byvalue:
            color = [
                meta.colors["full_shortcut"] if val > 0.0 else meta.colors["u"]
                for val in list(replay_metric[trajectory].values())
            ]
        else:
            color = meta.colors[trajectory]
        plt.bar(
            x + i * width,
            list(replay_metric[trajectory].values()),
            width=width,
            color=color,
        )

    # Add significance bars
    if pval is not None:
        h_adjust = (plt.ylim()[1] - plt.ylim()[0]) * 0.05
        if len(trajectories) == 2 and trajectories[0].endswith("u"):
            key = "exclusive" if trajectories[0].startswith("only_") else "overlapping"
            for i, xlabel in enumerate(orig_xlabels):
                significance_bar(
                    start=i - 0.05,
                    end=i + width + 0.05,
                    height=max(
                        replay_metric[trajectories[0]][xlabel],
                        replay_metric[trajectories[1]][xlabel],
                        0,
                    )
                    + h_adjust,
                    pval=pval[key][xlabel],
                )
        if len(trajectories) == 1 and trajectories[0] in ["difference", "contrast"]:
            key = "exclusive" if trajectories[0].startswith("only_") else "overlapping"
            for i, xlabel in enumerate(orig_xlabels):
                height = max(replay_metric[trajectories[0]][xlabel], 0) + h_adjust
                significance_text(
                    x=i,
                    height=height,
                    pval=pval[key][xlabel],
                )
        if len(trajectories) == 1 and trajectories[0] not in ["difference", "contrast"]:
            for (left, right), pp in pval[trajectories[0]].items():
                start = meta.task_times.index(left)
                end = meta.task_times.index(right)
                significance_bar(
                    start=start,
                    end=end,
                    height=max(
                        list(replay_metric[trajectories[0]].values())[start : end + 1]
                        + [0],
                    )
                    + h_adjust,
                    pval=pp,
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
