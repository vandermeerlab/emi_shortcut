import os

import matplotlib.pyplot as plt
import nept
import numpy as np
from matplotlib.colors import SymLogNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from shapely.geometry import Point

import meta
import meta_session
import paths
from plots import (
    plot_aligned_position_and_spikes,
    plot_by_standard_position,
    plot_raster,
)
from tasks import task


@task(infos=meta_session.analysis_infos, write_example_plots="run_raster")
def plot_run_raster(info, *, trials, tuning_curves, tc_spikes, example_plots):
    _plot_run_raster(
        info, trials, tuning_curves, tc_spikes, example_plots["run_raster"]
    )


@task(infos=meta_session.analysis_infos, write_example_plots="matched_run_raster")
def plot_matched_run_raster(
    info, *, trials, matched_tuning_curves, matched_tc_spikes, example_plots
):
    _plot_run_raster(
        info,
        trials,
        matched_tuning_curves,
        matched_tc_spikes,
        example_plots["matched_run_raster"],
    )


def _plot_run_raster(info, trials, tuning_curves, tc_spikes, example_plots):
    if meta.plot_all:
        for trajectory in meta.trajectories:
            # Early exit if no tuning curves with fields
            if len(tc_spikes[trajectory]) == 0:
                continue

            for i, trial in enumerate(trials[trajectory]):
                plot_raster(
                    [
                        spiketrain.time_slice(trial.start, trial.stop)
                        for spiketrain in tc_spikes[trajectory]
                    ],
                    (trial.start, trial.stop),
                    tuning_curves=tuning_curves[trajectory],
                    savepath=example_plots.savepath(info, trajectory, i),
                )
    else:
        for trajectory, i, savepath in example_plots.zip(info):
            trial = trials[trajectory][i]
            plot_raster(
                [
                    spiketrain.time_slice(trial.start, trial.stop)
                    for spiketrain in tc_spikes[trajectory]
                ],
                (trial.start, trial.stop),
                tuning_curves=tuning_curves[trajectory],
                savepath=savepath,
            )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        f"{traj}-{i}": ("tcs-matched", f"matched_tc_spikes_{traj}-{i}.svg")
        for i in range(3)
        for traj in meta.trajectories
    },
)
def plot_matched_tuning_spikes(
    info,
    *,
    position,
    position_byzone,
    raw_matched_linear,
    tc_matched_linear,
    matched_tc_spikes,
    matched_tuning_spikes,
    spikes,
    trials,
    lines,
    savepath,
):

    for trajectory in meta.trajectories:
        run_epoch = nept.run_threshold(
            tc_matched_linear[trajectory],
            thresh=meta.std_speed_limit,
            t_smooth=meta.std_t_smooth,
        )
        matched_start = lines[trajectory].interpolate(
            np.min(raw_matched_linear[trajectory].x)
        )
        matched_stop = lines[trajectory].interpolate(
            np.max(raw_matched_linear[trajectory].x)
        )

        plot_aligned_position_and_spikes(
            position=position,
            position_traj=position_byzone[trajectory],
            linear=tc_matched_linear[trajectory],
            linear_traj=tc_matched_linear[trajectory][run_epoch],
            spikes=matched_tc_spikes[trajectory],
            spikes_traj=matched_tuning_spikes[trajectory],
            epochs=trials[trajectory],
            color=meta.colors[trajectory],
            linear_ylim=(meta.tc_linear_bin_edges[0], meta.tc_linear_bin_edges[-1]),
            matched_ends=(matched_start, matched_stop),
            n_epochs=3,
            savepath=[
                path for key, path in savepath.items() if key.startswith(trajectory)
            ],
        )


@task(infos=meta_session.analysis_infos)
def plot_tuning_spikes(
    info,
    *,
    position,
    position_byzone,
    raw_linear,
    linear,
    tc_linear_restricted,
    tuning_spikes,
    tc_order,
    tc_spikes,
    trials,
    lines,
):

    for trajectory in meta.trajectories:
        n_trials = trials[trajectory].n_epochs
        savepath = [
            paths.plot_file(
                f"ind-{info.session_id}",
                "ind-spike-trials",
                f"trial-{trajectory}-{i}.svg",
            )
            for i in range(n_trials)
        ]
        os.makedirs(os.path.dirname(savepath[0]), exist_ok=True)

        plot_aligned_position_and_spikes(
            position=position,
            position_traj=position_byzone[trajectory],
            linear=linear[trajectory],
            linear_traj=tc_linear_restricted[trajectory],
            spikes=tc_spikes[trajectory],
            spikes_traj=tuning_spikes[trajectory],
            epochs=trials[trajectory],
            color=meta.colors[trajectory],
            matched_ends=(
                Point(*info.path_pts["feeder1"]),
                Point(*info.path_pts["feeder2"]),
            ),
            n_epochs=n_trials,
            savepath=savepath,
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-raw", f"raw_occupancy_{traj}.svg") for traj in meta.trajectories
    },
)
def plot_raw_occupancy(info, *, lines, raw_occupancy, savepath):
    for trajectory in meta.trajectories:
        feeder1 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder1"])
            )
            + meta.feeder_dist
        )
        feeder2 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            - meta.feeder_dist
        )

        fig, ax = plt.subplots(figsize=(8, 8))
        occ = raw_occupancy[trajectory]
        plt.plot(np.arange(occ.size) * meta.tc_binsize, occ, "o", lw=2)
        plt.axvline(feeder1, lw=1, c="k")
        plt.axvline(feeder2, lw=1, c="k")
        plt.axhline(np.median(occ[occ > 0]) * meta.min_occupancy, lw=1, c="k")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")

        plt.savefig(savepath[trajectory], bbox_inches="tight", transparent=True)
        plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath={traj: ("tcs", f"occupancy_{traj}.svg") for traj in meta.trajectories},
)
def plot_occupancy(info, *, occupancy, savepath):
    for trajectory in meta.trajectories:
        fig, ax = plt.subplots(figsize=(8, 8))
        occ = occupancy[trajectory]
        plt.plot(meta.tc_linear_bin_centers, occ, "o", lw=2)
        if info.full_standard_maze:
            plt.axvline(0, lw=1, c="k")
        else:
            plt.axvline(20, lw=1, c="k")
        plt.axvline(100, lw=1, c="k")
        plt.axhline(np.median(occ[occ > 0]) * meta.std_min_occupancy, lw=1, c="k")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")

        plt.savefig(savepath[trajectory], bbox_inches="tight", transparent=True)
        plt.close(fig)


# savepath here is a hack to ensure fig_tuning_curves can be automatically generated
@task(
    infos=meta_session.analysis_infos,
    savepath={traj: ("ind-tcs", f"tc_{traj}_18.svg") for traj in meta.trajectories},
)
def plot_tuning_spikes_position(
    info, *, task_times, position, tuning_curves, tuning_spikes_position, savepath
):
    for trajectory in meta.trajectories:
        _plot_tuning_spikes_position(
            info,
            task_times,
            position,
            tuning_curves[trajectory],
            tuning_spikes_position[trajectory],
            color=meta.colors[trajectory],
            filename=f"tc_{trajectory}",
        )


def _plot_tuning_spikes_position(
    info,
    task_times,
    position,
    tuning_curves,
    tuning_spikes_position,
    color=None,
    filename=None,
):
    assert filename is not None
    maze_position = position[task_times["maze_times"]]

    for i, (tuning_curve, spikes_position) in enumerate(
        zip(tuning_curves, tuning_spikes_position)
    ):
        fig = plt.figure(figsize=(13, 10))
        ax1 = fig.add_subplot(221)
        ax1.plot(
            maze_position.x, maze_position.y, "k.", ms=1, alpha=0.1, rasterized=True
        )
        ax1.plot(spikes_position.x, spikes_position.y, "r.", ms=10, rasterized=True)
        ax1.axis("off")

        ax2 = fig.add_subplot(222)
        ax2.plot(tuning_curve, color="k")
        ax2.set_xlabel("Linearized position bins", fontsize=meta.fontsize)
        ax2.set_ylabel("Mean firing rate (Hz)", fontsize=meta.fontsize)
        ax2.fill_between(
            np.arange(tuning_curve.size),
            tuning_curve,
            color=color if color is not None else "grey",
        )
        ax2.locator_params(axis="y", nbins=5)

        plt.setp(ax2.get_xticklabels(), fontsize=meta.fontsize)
        plt.setp(ax2.get_yticklabels(), fontsize=meta.fontsize)

        # Hide the right and top spines
        ax2.spines["right"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax2.yaxis.set_ticks_position("left")
        ax2.xaxis.set_ticks_position("bottom")

        # TODO: plot feeder location

        savepath = paths.plot_file(
            f"ind-{info.session_id}", "ind-tcs", f"{filename}_{i}.svg"
        )
        os.makedirs(os.path.dirname(savepath), exist_ok=True)

        plt.savefig(
            savepath,
            bbox_inches="tight",
            transparent=True,
            dpi=meta.rasterize_dpi,
        )
        plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-raw", f"raw_tc_mean_{traj}.svg") for traj in meta.trajectories
    },
)
def plot_raw_tc_mean(info, *, lines, raw_tc_mean, savepath):
    for trajectory in meta.trajectories:
        feeder1 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder1"])
            )
            + meta.feeder_dist
        )
        feeder2 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            - meta.feeder_dist
        )
        _plot_tc_mean(
            raw_tc_mean[trajectory],
            axvlines=[feeder1, feeder2],
            xlabel="Position bins",
            ylabel="Mean firing rate (Hz)",
            color=meta.colors[trajectory],
            title=meta.trajectories_labels[trajectory],
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-test", f"raw_test_tc_{traj}.svg") for traj in meta.trajectories
    },
)
def plot_raw_test_tc(info, *, lines, raw_test_tuning_curves, savepath):
    for trajectory in meta.trajectories:
        feeder1 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder1"])
            )
            + meta.feeder_dist
        )
        feeder2 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            - meta.feeder_dist
        )
        _plot_tc_mean(
            raw_test_tuning_curves[trajectory][0],
            axvlines=[feeder1, feeder2],
            xlabel="Position bins",
            ylabel="Firing rate (Hz)",
            color=meta.colors[trajectory],
            title=meta.trajectories_labels[trajectory],
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-test", f"raw_test_tc_mean_{traj}.svg") for traj in meta.trajectories
    },
)
def plot_raw_test_tc_mean(info, *, lines, raw_test_tc_mean, savepath):
    for trajectory in meta.trajectories:
        feeder1 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder1"])
            )
            + meta.feeder_dist
        )
        feeder2 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            - meta.feeder_dist
        )
        _plot_tc_mean(
            raw_test_tc_mean[trajectory],
            axvlines=[feeder1, feeder2],
            xlabel="Position bins",
            ylabel="Firing rate (Hz)",
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={traj: ("tcs-test", f"test_tc_{traj}.svg") for traj in meta.trajectories},
)
def plot_test_tc(info, *, lines, test_tuning_curves, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            test_tuning_curves[trajectory][0],
            xlabel="Linearized position bins",
            ylabel="Firing rate (Hz)",
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-test", f"test_tc_mean_{traj}.svg") for traj in meta.trajectories
    },
)
def plot_test_tc_mean(info, *, lines, test_tc_mean, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            test_tc_mean[trajectory],
            xlabel="Linearized position bins",
            ylabel="Firing rate (Hz)",
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-raw", f"raw_spike_count_mean_{traj}.svg")
        for traj in meta.trajectories
    },
)
def plot_raw_spike_count_mean(info, *, lines, raw_occupancy, raw_tc_mean, savepath):
    for trajectory in meta.trajectories:
        feeder1 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder1"])
            )
            + meta.feeder_dist
        )
        feeder2 = (
            lines[f"{trajectory}_with_feeders"].project(
                Point(*info.path_pts["feeder2"])
            )
            - meta.feeder_dist
        )
        _plot_tc_mean(
            raw_tc_mean[trajectory] * raw_occupancy[trajectory],
            axvlines=[feeder1, feeder2],
            xlabel="Position bins",
            ylabel="Spike count",
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={traj: ("tcs", f"tc_mean_{traj}.svg") for traj in meta.trajectories},
)
def plot_tc_mean(info, *, tc_mean, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            tc_mean[trajectory],
            xlabel="Linearized position bins",
            ylabel="Mean firing rate (Hz)",
            color=meta.colors[trajectory],
            title=meta.trajectories_labels[trajectory],
            savepath=savepath[trajectory],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs-matched", f"matched_tc_mean_{traj}.svg")
        for traj in meta.trajectories
    },
)
def plot_matched_tc_mean(info, *, matched_tc_mean, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            matched_tc_mean[trajectory],
            xlabel="Linearized position bins",
            ylabel="Mean firing rate (Hz)",
            savepath=savepath[trajectory],
        )


@task(infos=meta_session.analysis_infos, savepath=("tcs-joined", "joined_tc_mean.svg"))
def plot_joined_tc_mean(info, *, joined_tc_mean, savepath):
    _plot_tc_mean(
        joined_tc_mean,
        xlabel="Linearized position bins",
        ylabel="Mean firing rate (Hz)",
        savepath=savepath,
    )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: ("tcs", f"tc_mean_{traj}_normalized.svg") for traj in meta.trajectories
    },
)
def plot_tc_mean_normalized(info, *, tc_mean_normalized, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            tc_mean_normalized[trajectory],
            xlabel="Linearized position bins",
            ylabel="Mean normalized firing rate",
            savepath=savepath[trajectory],
        )


@task(
    groups=meta_session.groups,
    savepath={traj: ("tcs", f"tc_mean_{traj}.svg") for traj in meta.trajectories},
)
def plot_group_tc_mean(infos, group_name, *, tc_mean, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            tc_mean[trajectory],
            xlabel="Linearized position bins",
            ylabel="Mean firing rate (Hz)",
            color=meta.colors[trajectory],
            title=meta.trajectories_labels[trajectory],
            ylim=2.8 if group_name in ["all", "combined"] else None,
            savepath=savepath[trajectory],
        )


@task(
    groups=meta_session.groups,
    savepath={
        traj: ("tcs-matched", f"matched_tc_mean_{traj}.svg")
        for traj in meta.trajectories
    },
)
def plot_group_matched_tc_mean(infos, group_name, *, matched_tc_mean, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            matched_tc_mean[trajectory],
            xlabel="Linearized position bins",
            ylabel="Mean firing rate (Hz)",
            savepath=savepath[trajectory],
        )


@task(groups=meta_session.groups, savepath=("tcs-joined", "joined_tc_mean.svg"))
def plot_group_joined_tc_mean(infos, group_name, *, joined_tc_mean, savepath):
    _plot_tc_mean(
        joined_tc_mean,
        xlabel="Linearized position bins",
        ylabel="Mean firing rate (Hz)",
        savepath=savepath,
    )


@task(
    groups=meta_session.groups,
    savepath={
        traj: ("tcs", f"tc_mean_{traj}_normalized.svg") for traj in meta.trajectories
    },
)
def plot_group_tc_mean_normalized(infos, group_name, *, tc_mean_normalized, savepath):
    for trajectory in meta.trajectories:
        _plot_tc_mean(
            tc_mean_normalized[trajectory],
            xlabel="Linearized position bins",
            ylabel="Mean normalized firing rate",
            savepath=savepath[trajectory],
        )


def _plot_tc_mean(
    aggregate_tuning_curves,
    xlabel,
    ylabel,
    axvlines=None,
    color=None,
    title=None,
    txt=None,
    ylim=None,
    savepath=None,
):
    assert savepath is not None
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(aggregate_tuning_curves.size)
    if axvlines is not None:
        x *= meta.tc_binsize

    plt.plot(x, aggregate_tuning_curves, lw=1, color="k")
    ax.fill_between(
        x,
        aggregate_tuning_curves,
        color=color if color is not None else "grey",
    )
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.ylabel(ylabel, fontsize=meta.fontsize)
    plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
    plt.xlabel(xlabel, fontsize=meta.fontsize)
    plt.locator_params(axis="y", nbins=5)

    if axvlines is None:
        plt.xlim(-5, 105)
    else:
        for vline in axvlines:
            plt.axvline(vline, c="k", lw=1)

    if ylim is not None:
        plt.ylim(0, ylim)

    if title is not None:
        plt.title(title, fontsize=meta.fontsize)

    if txt is not None:
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

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


def _plot_tc_correlations_histogram(tc_correlations, savepath):
    fig, axs = plt.subplots(ncols=3, sharey=True, figsize=(18, 6.5))

    n_neurons = tc_correlations["phases12"].shape[0]

    for ax, phases in zip(axs, meta.phases_corr):
        if "proportion" in savepath:
            weights = np.ones_like(tc_correlations[phases]) / n_neurons
            ylabel = "Proportion of neurons"
        else:
            weights = None
            ylabel = "Number of neurons"
        x, bins, p = ax.hist(
            np.array(tc_correlations[phases]),
            bins=20,
            weights=weights,
            color=meta.colors["u"],
        )

        ax.set_title(f"Phases {phases[-2]}-{phases[-1]}", fontsize=meta.fontsize)

        plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
        ax.set_xlabel("Correlation value", fontsize=meta.fontsize)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.xaxis.set_ticks_position("bottom")
        plt.locator_params(axis="x", nbins=6)
        if ax is axs[0]:
            ax.text(
                0.05,
                0.95,
                f"Total n={n_neurons}",
                transform=ax.transAxes,
                horizontalalignment="left",
                verticalalignment="top",
                fontsize=meta.fontsize,
            )
            ax.set_ylabel(ylabel, fontsize=meta.fontsize)
            plt.locator_params(axis="y", nbins=6)
            plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
            ax.yaxis.set_ticks_position("left")
        else:
            ax.tick_params(labelleft=False)

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath={
        key: ("tcs", f"tc_correlations_{key}.svg") for key in ["count", "proportion"]
    },
)
def plot_tc_correlations_histogram(info, *, tc_correlations, savepath):
    for key in savepath:
        _plot_tc_correlations_histogram(
            tc_correlations,
            savepath=savepath[key],
        )


@task(
    groups=meta_session.groups,
    savepath={
        key: ("tcs", f"tc_correlations_{key}.svg") for key in ["count", "proportion"]
    },
)
def plot_group_tc_correlations_histogram(
    infos, group_name, *, tc_correlations, savepath
):
    for key in savepath:
        _plot_tc_correlations_histogram(
            tc_correlations,
            savepath=savepath[key],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        phases: ("tcs", f"tc_correlations_bybin_{phases}.svg")
        for phases in meta.phases_corr
    },
)
def plot_tc_correlations_bybin(info, *, tc_correlations_bybin, savepath):
    for phases in meta.phases_corr:
        plot_by_standard_position(
            value_bybin=tc_correlations_bybin[phases],
            ylabel="Correlation",
            color=meta.colors["u"],
            axvlines=meta.std_axvlines["u"],
            ylim=(-0.2, 1.0),
            savepath=savepath[phases],
        )


@task(
    groups=meta_session.groups,
    savepath={
        phases: ("tcs", f"tc_correlations_bybin_{phases}.svg")
        for phases in meta.phases_corr
    },
)
def plot_group_tc_correlations_bybin(
    infos, group_name, *, tc_correlations_bybin, savepath
):
    for phases in meta.phases_corr:
        plot_by_standard_position(
            value_bybin=tc_correlations_bybin[phases],
            ylabel="Correlation",
            color=meta.colors["u"],
            axvlines=meta.std_axvlines["u"],
            ylim=(-0.2, 1.0),
            savepath=savepath[phases],
        )


def _plot_tc_field_remapping(tc_fields_appear, tc_fields_disappear, savepath):
    n_neurons = tc_fields_appear["phases12"].size
    n_appear = {phases: np.sum(tc_fields_appear[phases]) for phases in meta.phases_corr}
    n_disappear = {
        phases: np.sum(tc_fields_disappear[phases]) for phases in meta.phases_corr
    }
    prop_appear = {phases: n_appear[phases] / n_neurons for phases in meta.phases_corr}
    prop_disappear = {
        phases: n_disappear[phases] / n_neurons for phases in meta.phases_corr
    }

    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(2)
    width = 0.8 / 2
    plt.bar(
        x,
        [prop_appear["phases12"], prop_appear["phases23"]],
        width=width,
        color=meta.colors["u"],
        label="Appear",
    )
    plt.bar(
        x + width,
        [prop_disappear["phases12"], prop_disappear["phases23"]],
        width=width,
        color=meta.colors["contrast"],
        label="Disappear",
    )
    top = plt.ylim()[1]
    textargs = {
        "color": "w",
        "y": top * 0.01,
        "horizontalalignment": "center",
        "verticalalignment": "bottom",
        "fontsize": meta.fontsize,
    }

    ax.text(x=0, s=f"{n_appear['phases12']}", **textargs)
    ax.text(x=0.4, s=f"{n_disappear['phases12']}", **textargs)
    ax.text(x=1, s=f"{n_appear['phases23']}", **textargs)
    ax.text(x=1.4, s=f"{n_disappear['phases23']}", **textargs)

    offset = 0.2
    plt.xticks(x + offset, ["Phase 2", "Phase 3"], fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.locator_params(axis="y", nbins=5)
    plt.ylabel("Proportion of remapping neurons", fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.legend(fontsize=meta.fontsize_small)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")

    plt.tight_layout()
    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(infos=meta_session.analysis_infos, savepath=("tcs", "tc_field_remapping.svg"))
def plot_tc_field_remapping(info, *, tc_fields_appear, tc_fields_disappear, savepath):
    _plot_tc_field_remapping(tc_fields_appear, tc_fields_disappear, savepath)


@task(
    groups=meta_session.groups,
    savepath=("tcs", "tc_field_remapping.svg"),
)
def plot_group_tc_field_remapping(
    infos, group_name, *, tc_fields_appear, tc_fields_disappear, savepath
):
    _plot_tc_field_remapping(tc_fields_appear, tc_fields_disappear, savepath)


def _plot_tc_mean_comparison(
    tc_mean, tc_mean_remapped, label, color=None, title=None, savepath=None
):
    assert savepath is not None
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(tc_mean, lw=1, color="grey", label="All TCs")
    ax.fill_between(
        np.arange(tc_mean.size),
        0,
        tc_mean,
        color="grey",
        alpha=0.4,
    )

    plt.plot(tc_mean_remapped, lw=1, color=meta.colors["u"], label=label)
    for axvline in meta.std_axvlines["u"]:
        ax.axvline(axvline, linestyle="dashed", color="k")
    ax.fill_between(
        np.arange(tc_mean_remapped.size),
        0,
        tc_mean_remapped,
        color=meta.colors["u"],
        alpha=0.4,
    )
    if "normalized" in savepath:
        ax.set_ylabel("Mean normalized firing rate", fontsize=meta.fontsize)
    else:
        ax.set_ylabel("Mean firing rate (Hz)", fontsize=meta.fontsize)

    ax.set_xlabel("Linearized position bins", fontsize=meta.fontsize)
    plt.legend(fontsize=meta.fontsize_small)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.set_ticks_position("bottom")
    plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
    plt.setp(ax.get_yticklabels(), fontsize=meta.fontsize)
    plt.locator_params(axis="y", nbins=5)

    plt.tight_layout(h_pad=0.003)

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath={
        phase: ("tcs", f"tc_mean_appear_{phase}.svg")
        for phase in meta.run_times
        if phase != "phase1"
    },
)
def plot_tc_mean_appear(info, *, u_tcs_byphase_mean, tc_appear_mean, savepath):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean[phase],
            tc_appear_mean[f"phases{'12' if phase == 'phase2' else '23'}"],
            label="Appearing TCs",
            savepath=savepath[phase],
        )


@task(
    groups=meta_session.groups,
    savepath={
        phase: ("tcs", f"tc_mean_appear_{phase}.svg")
        for phase in meta.run_times
        if phase != "phase1"
    },
)
def plot_group_tc_mean_appear(
    infos, group_name, *, u_tcs_byphase_mean, tc_appear_mean, savepath
):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean[phase],
            tc_appear_mean[f"phases{'12' if phase == 'phase2' else '23'}"],
            label="Appearing TCs",
            savepath=savepath[phase],
        )


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        phase: ("tcs", f"tc_appear_maxpeaks_{phase}.svg")
        for phase in meta.run_times
        if phase != "phase1"
    },
)
def plot_group_tc_appear_maxpeaks(infos, group_name, *, tc_appear_maxpeaks, savepath):
    for phase in savepath:
        plot_by_standard_position(
            value_bybin=tc_appear_maxpeaks[
                f"phases{'12' if phase == 'phase2' else '23'}"
            ],
            ylabel="Count of appearing neurons",
            color=meta.colors["u"],
            axvlines=meta.std_axvlines["u"],
            ylim=(0, 12),
            title=meta.task_times_labels[phase],
            savepath=savepath[phase],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        phase: ("tcs", f"tc_mean_appear_{phase}_normalized.svg")
        for phase in meta.run_times
        if phase != "phase1"
    },
)
def plot_tc_mean_appear_normalized(
    info, *, u_tcs_byphase_mean_normalized, tc_appear_mean_normalized, savepath
):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean_normalized[phase],
            tc_appear_mean_normalized[f"phases{'12' if phase == 'phase2' else '23'}"],
            label="Appearing TCs",
            savepath=savepath[phase],
        )


@task(
    groups=meta_session.groups,
    savepath={
        phase: ("tcs", f"tc_mean_appear_{phase}_normalized.svg")
        for phase in meta.run_times
        if phase != "phase1"
    },
)
def plot_group_tc_mean_appear_normalized(
    infos,
    group_name,
    *,
    u_tcs_byphase_mean_normalized,
    tc_appear_mean_normalized,
    savepath,
):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean_normalized[phase],
            tc_appear_mean_normalized[f"phases{'12' if phase == 'phase2' else '23'}"],
            label="Appearing TCs",
            savepath=savepath[phase],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        phase: ("tcs", f"tc_mean_disappear_{phase}.svg")
        for phase in meta.run_times
        if phase != "phase3"
    },
)
def plot_tc_mean_disappear(info, *, u_tcs_byphase_mean, tc_disappear_mean, savepath):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean[phase],
            tc_disappear_mean[f"phases{'12' if phase == 'phase1' else '23'}"],
            label="Disappearing TCs",
            savepath=savepath[phase],
        )


@task(
    groups=meta_session.groups,
    savepath={
        phase: ("tcs", f"tc_mean_disappear_{phase}.svg")
        for phase in meta.run_times
        if phase != "phase3"
    },
)
def plot_group_tc_mean_disappear(
    infos, group_name, *, u_tcs_byphase_mean, tc_disappear_mean, savepath
):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean[phase],
            tc_disappear_mean[f"phases{'12' if phase == 'phase1' else '23'}"],
            label="Disappearing TCs",
            savepath=savepath[phase],
        )


@task(
    groups=meta_session.analysis_grouped,
    savepath={
        phase: ("tcs", f"tc_disappear_maxpeaks_{phase}.svg")
        for phase in meta.run_times
        if phase != "phase3"
    },
)
def plot_group_tc_disappear_maxpeaks(
    infos, group_name, *, tc_disappear_maxpeaks, savepath
):
    for phase in savepath:
        plot_by_standard_position(
            value_bybin=tc_disappear_maxpeaks[
                f"phases{'12' if phase == 'phase1' else '23'}"
            ],
            ylabel="Count of disappearing neurons",
            color=meta.colors["u"],
            axvlines=meta.std_axvlines["u"],
            ylim=(0, 12),
            title=meta.task_times_labels[phase],
            savepath=savepath[phase],
        )


@task(
    infos=meta_session.analysis_infos,
    savepath={
        phase: ("tcs", f"tc_mean_disappear_{phase}_normalized.svg")
        for phase in meta.run_times
        if phase != "phase3"
    },
)
def plot_tc_mean_disappear_normalized(
    info, *, u_tcs_byphase_mean_normalized, tc_disappear_mean_normalized, savepath
):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean_normalized[phase],
            tc_disappear_mean_normalized[
                f"phases{'12' if phase == 'phase1' else '23'}"
            ],
            label="Disappearing TCs",
            savepath=savepath[phase],
        )


@task(
    groups=meta_session.groups,
    savepath={
        phase: ("tcs", f"tc_mean_disappear_{phase}_normalized.svg")
        for phase in meta.run_times
        if phase != "phase3"
    },
)
def plot_group_tc_mean_disappear_normalized(
    infos,
    group_name,
    *,
    u_tcs_byphase_mean_normalized,
    tc_disappear_mean_normalized,
    savepath,
):
    for phase in savepath:
        _plot_tc_mean_comparison(
            u_tcs_byphase_mean_normalized[phase],
            tc_disappear_mean_normalized[
                f"phases{'12' if phase == 'phase1' else '23'}"
            ],
            label="Disappearing TCs",
            savepath=savepath[phase],
        )


def _plot_tc_correlations_within_phase(tc_correlations_within_phase, savepath):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=[15, 5])
    for ax, phase in zip((ax1, ax2, ax3), meta.run_times):
        im = ax.imshow(
            tc_correlations_within_phase[phase],
            cmap="inferno",
            interpolation="nearest",
            vmin=0,
            vmax=1,
        )
        ax.set_title(meta.task_times_labels[phase], y=1.08, fontsize=meta.fontsize)
        ax.set_xlabel("Linearized position bins", fontsize=meta.fontsize)

        trans = ax.get_xaxis_transform()  # x in data units, y in axes units
        for xx in meta.std_axvlines["u"]:
            ax.annotate(
                " ",
                xy=(xx, 1.0),
                xytext=(xx, 1.07),
                textcoords=trans,
                xycoords=trans,
                arrowprops=dict(arrowstyle="->", lw=2, connectionstyle="angle"),
            )
        ax.tick_params(labelsize=meta.fontsize)
        ax.set_xticks(meta.ticks)
        ax.set_yticks(meta.ticks)

    ax1.set_ylabel("Linearized position bins", fontsize=meta.fontsize)

    axins = inset_axes(
        ax3,
        width="5%",  # width = 5% of parent_bbox width
        height="70%",  # height : 50%
        loc="lower left",
        bbox_to_anchor=(1.05, 0.0, 1, 1),
        bbox_transform=ax3.transAxes,
        borderpad=0,
    )
    cbar = fig.colorbar(im, cax=axins)
    cbar.ax.tick_params(labelsize=meta.fontsize)

    plt.tight_layout(h_pad=0.003)
    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath=("tcs", "tc_correlations_within_phase.svg"),
)
def plot_tc_correlations_within_phase(info, *, tc_correlations_within_phase, savepath):
    _plot_tc_correlations_within_phase(tc_correlations_within_phase, savepath)


@task(
    groups=meta_session.groups,
    savepath=("tcs", "tc_correlations_within_phase.svg"),
)
def plot_group_tc_correlations_within_phase(
    infos, group_name, *, tc_correlations_within_phase, savepath
):
    _plot_tc_correlations_within_phase(tc_correlations_within_phase, savepath)


@task(infos=meta_session.analysis_infos)
def plot_tcs_2d_heatmap(info, *, tuning_spikes_histogram):
    plot_log = False
    vmax = None

    # TODO: add example_plots stuff to this
    if meta.plot_all:
        for trajectory in meta.trajectories:
            all_hist = np.mean(tuning_spikes_histogram[trajectory], axis=1)
            all_hist = np.ma.masked_equal(all_hist, 0)
            plt.pcolormesh(all_hist, cmap="Greys")
            for i, tc_hist in enumerate(tuning_spikes_histogram[trajectory]):
                tc_hist = np.ma.masked_equal(tc_hist, 0)
                fig, ax = plt.subplots(figsize=(6, 6))
                plt.figure(figsize=(5, 4))

                if plot_log:
                    pp = plt.pcolormesh(
                        tc_hist,
                        norm=SymLogNorm(linthresh=1.0, vmax=vmax),
                        cmap="YlGn",
                    )
                else:
                    pp = plt.pcolormesh(tc_hist, vmax=vmax, cmap="YlGn")
                plt.colorbar(pp)
                plt.axis("off")

                savepath = paths.plot_file(
                    f"ind-{info.session_id}",
                    "ind-tcs-2d",
                    f"tc-2d-{trajectory}-{i}.svg",
                )
                os.makedirs(os.path.dirname(savepath), exist_ok=True)

                plt.tight_layout(h_pad=0.003)
                plt.savefig(savepath, bbox_inches="tight", transparent=True)
                plt.close(fig)
