import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point

import meta
import meta_session
from tasks import task


@task(infos=meta_session.all_infos, savepath=("mazes", "maze.svg"))
def plot_maze(info, *, lines, savepath):
    fig = plt.figure()
    for trajectory, line in lines.items():
        if trajectory.endswith("_with_feeders"):
            continue
        x, y = line.xy
        plt.plot(x, y, c=meta.colors[trajectory])
        for pt in line.coords:
            plt.plot(pt[0], pt[1], "ko")
    plt.tight_layout()

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)


@task(
    infos=meta_session.analysis_infos,
    savepath={
        traj: (
            "mazes",
            f"zone-{traj}.svg",
        )
        for traj in meta.trajectories
    },
)
def plot_zone(info, *, position, position_byzone, lines, zones, savepath):
    for trajectory in meta.trajectories:
        feeders = [zones[f"{trajectory}_feeder1"], zones[f"{trajectory}_feeder2"]]
        fig = plt.figure()
        plt.plot(position.x, position.y, ".", ms=3, color="k", rasterized=True)
        subposition = position_byzone[trajectory]
        line = lines[trajectory]
        zone = zones[trajectory]
        color = meta.colors[trajectory]

        plt.plot(subposition.x, subposition.y, ".", ms=3, color=color, rasterized=True)

        for pt in line.coords:
            text = plt.text(
                pt[0],
                pt[1],
                "{:.0f}".format(line.project(Point(*pt))),
                color="white",
                fontsize="small",
                ha="center",
                va="center",
            )
            text.set_path_effects(
                [
                    path_effects.Stroke(linewidth=3, foreground="black"),
                    path_effects.Normal(),
                ]
            )

        for polygon in [zone] + feeders:
            c = "k" if polygon is zone else "r"
            if (
                polygon.geom_type == "MultiPolygon"
                or polygon.geom_type == "GeometryCollection"
            ):
                for intersect in polygon:
                    x, y = intersect.exterior.xy
                    plt.plot(x, y, c, lw=1)
            else:
                x, y = polygon.exterior.xy
            plt.plot(x, y, c, lw=1)
        plt.tight_layout()

        assert trajectory in savepath
        plt.savefig(
            savepath[trajectory],
            bbox_inches="tight",
            transparent=True,
            dpi=meta.rasterize_dpi,
        )
        plt.close(fig)


@task(
    groups=meta_session.groups,
    savepath={
        traj: ("mazes", f"std_distortion_{traj}.svg") for traj in meta.trajectories
    },
)
def plot_std_distortion(infos, group_name, *, all_lines, savepath):
    for trajectory in meta.trajectories:
        fig, ax = plt.subplots(figsize=(8, 6))

        edges = []
        for info, lines in zip(infos, all_lines):
            line = lines[trajectory]
            edges.append(
                [
                    line.project(Point(info.path_pts["feeder1"])),
                    line.project(Point(info.path_pts["shortcut1"])),
                    line.project(Point(info.path_pts["shortcut2"])),
                    line.project(Point(info.path_pts["feeder2"])),
                ]
            )
            if trajectory == "u":
                edges[-1].insert(2, line.project(Point(info.path_pts["turn1"])))
                edges[-1].insert(3, line.project(Point(info.path_pts["turn2"])))
        edges = np.array(edges).T
        # subtract midpoint between shortcut pts to align middles
        if trajectory == "u":
            edges -= (edges[2] + edges[3]) / 2
        else:
            edges -= (edges[1] + edges[2]) / 2

        y = np.arange(len(infos))
        for i in range(edges.shape[0] - 1):
            if i == 0 or i == edges.shape[0] - 2:
                color = meta.colors["contrast"]
            elif trajectory == "u" and i == 2:
                color = meta.colors["light_u"]
            else:
                color = meta.colors[trajectory]
            ax.barh(
                y,
                left=edges[i],
                width=edges[i + 1] - edges[i],
                color=color,
            )
        ax.axvline(c="k")
        ax.set_ylim(y[0] - 0.8, y[-1] + 0.8)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        plt.setp(ax.get_xticklabels(), fontsize=meta.fontsize)
        plt.xlabel("Linear position (cm)", fontsize=meta.fontsize)
        plt.title(meta.trajectories_labels[trajectory], fontsize=meta.fontsize)

        plt.tight_layout()
        plt.savefig(
            savepath[trajectory],
            bbox_inches="tight",
            transparent=True,
        )
        plt.close(fig)
