import matplotlib.pyplot as plt
import numpy as np

import meta
import meta_session
from tasks import task


@task(infos=meta_session.all_infos, savepath=("mazes", "maze_matched.svg"))
def plot_matched_ends_on_maze(info, *, lines_matched, savepath):
    fig, ax = plt.subplots(figsize=(6, 5))
    for trajectory, line in lines_matched.items():
        if trajectory.endswith("_with_feeders"):
            continue
        x, y = line.xy
        plt.plot(x, y, c="k", lw=3)

    for trajectory in meta.matched_trajectories:
        x, y = lines_matched[trajectory].xy
        plt.plot(x, y, c=meta.colors[trajectory], lw=6)
        start = lines_matched[trajectory].coords[0]
        end = lines_matched[trajectory].coords[-1]
        plt.plot(start[0], start[1], "o", ms=20, color=meta.colors[trajectory])
        plt.plot(end[0], end[1], "o", ms=20, color=meta.colors[trajectory])

    plt.title("Example session", fontsize=meta.fontsize)
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)
