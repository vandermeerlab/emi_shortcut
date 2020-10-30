import matplotlib.pyplot as plt
import numpy as np

import meta
import meta_session
from tasks import task


@task(infos=meta_session.all_infos, savepath=("mazes", "maze_matched.svg"))
def plot_matched_ends_on_maze(info, *, lines, raw_matched_linear, savepath):
    fig, ax = plt.subplots(figsize=(6, 5))
    for trajectory, line in lines.items():
        if trajectory.endswith("_with_feeders"):
            continue
        x, y = line.xy
        plt.plot(x, y, c="k", lw=6)

    for trajectory in meta.trajectories:
        linear = raw_matched_linear[trajectory]
        start = lines[trajectory].interpolate(np.min(linear.x))
        end = lines[trajectory].interpolate(np.max(linear.x))
        plt.plot(start.x, start.y, "o", ms=20, color=meta.colors[trajectory])
        plt.plot(end.x, end.y, "o", ms=20, color=meta.colors[trajectory])

    plt.title("Example session", fontsize=meta.fontsize)
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(savepath, bbox_inches="tight", transparent=True)
    plt.close(fig)
