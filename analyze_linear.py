import nept
import numpy as np
from shapely.geometry import Point

import meta
import meta_session
from tasks import task
from utils import map_range


@task(infos=meta_session.all_infos, cache_saves="raw_linear")
def cache_raw_linear(info, *, position_byzone, lines):
    """Cache raw linearized position in .pkl"""
    linear = {}
    for trajectory in meta.trajectories:
        full_line = lines[f"{trajectory}_with_feeders"]

        feeder1 = f"{trajectory}_feeder1"
        linear[feeder1] = position_byzone[feeder1].linearize(full_line)
        linear[trajectory] = position_byzone[trajectory].linearize(full_line)
        feeder2 = f"{trajectory}_feeder2"
        linear[feeder2] = position_byzone[feeder2].linearize(full_line)
        linear[f"{trajectory}_with_feeders"] = (
            linear[feeder1].combine(linear[trajectory]).combine(linear[feeder2])
        )

    return linear


@task(infos=meta_session.all_infos, cache_saves="raw_matched_linear")
def cache_raw_matched_linear(info, *, raw_linear, lines):
    u_start = lines["u"].project(Point(info.path_pts["shortcut1"]))
    u_end = lines["u"].project(Point(info.path_pts["shortcut2"]))
    u_dist = u_end - u_start
    assert u_dist > 0, "u_end is past u_start"

    full_shortcut_offset = lines["full_shortcut_feeder1"].length
    full_shortcut_start = np.min(raw_linear["full_shortcut"].x) - full_shortcut_offset
    full_shortcut_end = np.max(raw_linear["full_shortcut"].x) - full_shortcut_offset
    full_shortcut_dist = full_shortcut_end - full_shortcut_start
    assert full_shortcut_dist > 0, "full_shortcut_end is past full_shortcut_start"

    # Check if we're in the weird case that shortening the full_shortcut would
    # result in rebalancing past the original start/end
    full_shortcut_barriers = [
        lines["full_shortcut"].project(Point(info.path_pts["shortcut1"])),
        lines["full_shortcut"].project(Point(info.path_pts["shortcut2"])),
    ]
    full_shortcut_midpoint = sum(full_shortcut_barriers) / 2
    if full_shortcut_dist > u_dist:
        half_dist = u_dist / 2
        if full_shortcut_midpoint - half_dist < full_shortcut_start:
            dist = full_shortcut_barriers[0] - full_shortcut_start
            assert full_shortcut_barriers[1] + dist < full_shortcut_end
            full_shortcut_end = full_shortcut_barriers[1] + dist
        elif full_shortcut_midpoint + half_dist > full_shortcut_end:
            dist = full_shortcut_end - full_shortcut_barriers[1]
            assert full_shortcut_barriers[0] - dist > full_shortcut_start
            full_shortcut_start = full_shortcut_barriers[0] - dist
        full_shortcut_dist = full_shortcut_end - full_shortcut_start

    # Now we can rebalance as normal
    if full_shortcut_dist > u_dist:
        midpoint = (
            lines["full_shortcut"].project(Point(info.path_pts["shortcut1"]))
            + lines["full_shortcut"].project(Point(info.path_pts["shortcut2"]))
        ) / 2
        half_dist = u_dist / 2
        full_shortcut_start = midpoint - half_dist
        full_shortcut_end = midpoint + half_dist
    else:
        assert u_dist > full_shortcut_dist
        midpoint = (u_end + u_start) / 2
        half_dist = full_shortcut_dist / 2
        u_start = midpoint - half_dist
        u_end = midpoint + half_dist

    # Add some extra points to deal with tuning curves falling off at the edges
    binsize = (half_dist * 2) / 100
    u_start -= meta.tc_extra_bins_before * binsize
    u_end += meta.tc_extra_bins_after * binsize
    full_shortcut_start -= meta.tc_extra_bins_before * binsize
    full_shortcut_end += meta.tc_extra_bins_after * binsize

    raw_u = raw_linear["u"]
    matched_u = raw_u[(raw_u.x >= u_start) & (raw_u.x <= u_end)]
    raw_full_shortcut = raw_linear["full_shortcut"]
    raw_full_shortcut.x -= full_shortcut_offset
    matched_full_shortcut = raw_full_shortcut[
        (raw_full_shortcut.x >= full_shortcut_start)
        & (raw_full_shortcut.x <= full_shortcut_end)
    ]
    return {"u": matched_u, "full_shortcut": matched_full_shortcut}


@task(infos=meta_session.all_infos, cache_saves="tc_matched_linear")
def cache_tc_matched_linear(info, *, raw_matched_linear):
    matched_linear = raw_matched_linear
    for trajectory in matched_linear:
        traj_linear = matched_linear[trajectory]
        traj_linear.x[...] = map_range(
            traj_linear.x,
            from_min=np.min(traj_linear.x),
            from_max=np.max(traj_linear.x),
            to_min=meta.tc_linear_bin_edges[0],
            to_max=meta.tc_linear_bin_edges[-1],
        )

    return matched_linear


@task(infos=meta_session.all_infos, cache_saves="matched_linear")
def cache_matched_linear(info, *, tc_matched_linear):
    return {
        trajectory: tc_matched_linear[trajectory][
            (tc_matched_linear[trajectory].x >= meta.linear_bin_edges[0])
            & (tc_matched_linear[trajectory].x <= meta.linear_bin_edges[-1])
        ]
        for trajectory in meta.trajectories
    }


@task(infos=meta_session.all_infos, cache_saves="joined_linear")
def cache_joined_linear(info, *, matched_linear):
    joined_linear = nept.Position(
        map_range(matched_linear["u"].x, from_min=0, from_max=100, to_min=0, to_max=50),
        matched_linear["u"].time,
    )
    return joined_linear.combine(
        nept.Position(
            map_range(
                matched_linear["full_shortcut"].x,
                from_min=0,
                from_max=100,
                to_min=50,
                to_max=100,
            ),
            matched_linear["full_shortcut"].time,
        )
    )


def standardize_segment(info, x, out, line, start, stop):
    if info.full_standard_maze:
        standard_points = meta.full_standard_points
    else:
        standard_points = meta.short_standard_points

    if start == "min":
        from_min = np.amin(x)
    else:
        from_min = line.project(Point(info.path_pts[start]))

    if stop == "max":
        from_max = np.amax(x)
    else:
        from_max = line.project(Point(info.path_pts[stop]))

    if start == "feeder1":
        from_min += meta.feeder_dist
    if stop == "feeder1":
        from_max += meta.feeder_dist
    if start == "feeder2":
        from_min -= meta.feeder_dist
    if stop == "feeder2":
        from_max -= meta.feeder_dist

    idx = (x >= from_min) & (x <= from_max)
    out[idx] = map_range(
        x[idx],
        from_min=from_min,
        from_max=from_max,
        to_min=standard_points[start],
        to_max=standard_points[stop],
    )


@task(infos=meta_session.all_infos, cache_saves="tc_linear")
def cache_tc_linear(info, *, raw_linear, lines):
    """Cache standard linear in .pkl"""
    linear = {
        trajectory: raw_linear[f"{trajectory}_feeder1"]
        .combine(raw_linear[trajectory])
        .combine(raw_linear[f"{trajectory}_feeder2"])
        for trajectory in meta.trajectories
    }

    full_line = lines["u_with_feeders"]
    out = linear["u"].x
    x = np.array(out)
    standardize_segment(info, x, out, full_line, "min", "feeder1")
    if info.full_standard_maze:
        standardize_segment(info, x, out, full_line, "feeder1", "shortcut1")
        standardize_segment(info, x, out, full_line, "shortcut1", "turn1")
    else:
        assert info.path_pts["feeder1"] == info.path_pts["shortcut1"]
        standardize_segment(info, x, out, full_line, "feeder1", "turn1")

    standardize_segment(info, x, out, full_line, "turn1", "turn2")
    standardize_segment(info, x, out, full_line, "turn2", "shortcut2")
    standardize_segment(info, x, out, full_line, "shortcut2", "feeder2")
    standardize_segment(info, x, out, full_line, "feeder2", "max")

    full_line = lines["full_shortcut_with_feeders"]
    out = linear["full_shortcut"].x
    x = np.array(out)
    standardize_segment(info, x, out, full_line, "min", "feeder1")
    if info.full_standard_maze:
        standardize_segment(info, x, out, full_line, "feeder1", "shortcut1")
        standardize_segment(info, x, out, full_line, "shortcut1", "shortcut2")
    else:
        standardize_segment(info, x, out, full_line, "feeder1", "shortcut2")

    standardize_segment(info, x, out, full_line, "shortcut2", "feeder2")
    standardize_segment(info, x, out, full_line, "feeder2", "max")

    return linear


@task(infos=meta_session.all_infos, cache_saves="linear")
def cache_linear(info, *, tc_linear):
    if info.full_standard_maze:
        standard_points = meta.full_standard_points
    else:
        standard_points = meta.short_standard_points
    return {
        trajectory: tc_linear[trajectory][
            (tc_linear[trajectory].x >= standard_points["feeder1"])
            & (tc_linear[trajectory].x <= standard_points["feeder2"])
        ]
        for trajectory in meta.trajectories
    }
