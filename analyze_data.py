import os
import warnings
import zipfile

import nept
import numpy as np
import scipy
from shapely.geometry import CAP_STYLE, LineString, Point

import meta
import meta_session
import paths
from tasks import task

warnings.filterwarnings("ignore")


def extract_xy(target):
    """Extracts x and y from neuralynx target. Converts to cm.

    Parameters
    ----------
    target: np.array

    Returns
    -------
    x: np.array
    y: np.array

    """
    binary_target = "{:032b}".format(target)
    x = int(binary_target[20:31], 2)
    y = int(binary_target[4:15], 2)

    return x, y


def median_filter(x, y, kernel):
    # Applying a median filter to the x and y positions

    x = scipy.signal.medfilt(x, kernel_size=kernel)
    y = scipy.signal.medfilt(y, kernel_size=kernel)

    return x, y


def zip_nvt_file(datapath, filename):
    """Compresses a videotracking (*.nvt) file

    Parameters
    ----------
    datapath: str
    filename: str

    """
    file = zipfile.ZipFile(os.path.join(datapath, filename + ".zip"), "w")
    file.write(
        os.path.join(datapath, filename + ".nvt"),
        filename + ".nvt",
        compress_type=zipfile.ZIP_DEFLATED,
    )

    file.close()


def unzip_nvt_file(datapath, filename):
    """Extracts a videotracking (*.nvt) file

    Parameters
    ----------
    datapath: str
    filename: str

    """
    with zipfile.ZipFile(os.path.join(datapath, f"{filename}.zip"), "r") as file:
        file.extractall(datapath)


def load_shortcut_position(
    info, filename, events, task_times, dist_thresh=20.0, std_thresh=2.0
):
    """Loads and corrects shortcut position.

    Parameters
    ----------
    info: module
    filename: str
    events: dict
    dist_thresh: float
    std_thresh: float

    Returns
    -------
    position: nept.Position

    """
    # Load raw position from file
    nvt_data = nept.load_nvt(filename, remove_empty=False)
    targets = nvt_data["targets"]
    times = nvt_data["time"]

    # Initialize x, y arrays
    x = np.zeros(targets.shape)
    y = np.zeros(targets.shape)

    # X and Y are stored in a custom bitfield. See Neuralynx data file format
    # documentation for details.
    # Briefly, each record contains up to 50 targets, each stored in 32bit field.
    # X field at [20:31] and Y at [4:15].
    # TODO: make into a separate function in nept
    for target in range(targets.shape[1]):
        this_sample = targets[:, target]
        for sample in range(targets.shape[0]):
            # When the bitfield is equal to zero there is no valid data for that field
            # and remains zero for the rest of the bitfields in the record.
            if this_sample[target] == 0:
                break
            x[sample, target], y[sample, target] = extract_xy(int(this_sample[sample]))

    # Replacing targets with no samples with nan instead of 0
    x[x == 0] = np.nan
    y[y == 0] = np.nan

    # Scale the positions
    x /= info.scale_targets
    y /= info.scale_targets

    off_delay = np.median(np.diff(times))

    # Finding which feeder led is on over time
    leds = []
    leds.extend([(event, "led1") for event in events["led1"]])
    leds.extend([(event, "led2") for event in events["led2"]])
    sorted_leds = sorted(leds)

    ledoff = events["ledoff"]

    # Get an array of feeder locations when that feeder is actively flashing
    feeder_x_location = np.empty(times.shape[0]) * np.nan
    feeder_y_location = np.empty(times.shape[0]) * np.nan

    off_idx = 0

    for start, label in sorted_leds:
        # Find next off idx
        while off_idx < len(ledoff) and ledoff[off_idx] < start:
            off_idx += 1

        # Discount the last event when last off missing
        if off_idx >= len(ledoff):
            break

        x_location = (
            info.path_pts["feeder1"][0]
            if label == "led2"
            else info.path_pts["feeder2"][0]
        )
        y_location = (
            info.path_pts["feeder1"][1]
            if label == "led2"
            else info.path_pts["feeder2"][1]
        )

        feeder_x_location[
            np.logical_and(
                times >= start - off_delay, times < ledoff[off_idx] + off_delay
            )
        ] = x_location
        feeder_y_location[
            np.logical_and(
                times >= start - off_delay, times < ledoff[off_idx] + off_delay
            )
        ] = y_location

    # Remove problem samples for individual session
    if info.session_id in ["R063d8", "R068d4", "R068d5", "R068d6"]:
        starts_idx = nept.find_nearest_indices(times, info.problem_positions.starts)
        stops_idx = nept.find_nearest_indices(times, info.problem_positions.stops)
        for start, stop in zip(starts_idx, stops_idx):
            x[start:stop] = np.nan
            y[start:stop] = np.nan

    # Remove problem samples for individual session
    # In impossible locations and along the u-trajectory for R066d7
    if info.session_id == "R066d7":
        for error_pt in info.path_pts["error"]:
            x_idx = np.abs(x - error_pt[0]) <= 20.0
            y_idx = np.abs(y - error_pt[1]) <= 20.0
            remove_idx = x_idx & y_idx

            x[remove_idx] = np.nan
            y[remove_idx] = np.nan

        starts_idx = nept.find_nearest_indices(times, info.problem_positions.starts)
        stops_idx = nept.find_nearest_indices(times, info.problem_positions.stops)
        for start, stop in zip(starts_idx, stops_idx):
            x_idx = x[start:stop] <= 100.0
            y_idx = y[start:stop] <= 60.0
            remove_idx = x_idx & y_idx

            x[start:stop][remove_idx] = np.nan
            y[start:stop][remove_idx] = np.nan

    # Remove problem samples for individual session
    # While both LEDs are active for R067d1
    if info.session_id == "R067d1":
        starts_idx = nept.find_nearest_indices(times, info.problem_positions.starts)
        stops_idx = nept.find_nearest_indices(times, info.problem_positions.stops)
        for start, stop in zip(starts_idx, stops_idx):
            feeder_x_location[start:stop] = np.nan
            feeder_y_location[start:stop] = np.nan

    # Remove problem samples for individual session
    # In impossible locations for R068d3
    if info.session_id == "R068d3":
        for error_pt in info.path_pts["error"]:
            x_idx = np.abs(x - error_pt[0]) <= 10.0
            y_idx = np.abs(y - error_pt[1]) <= 10.0
            remove_idx = x_idx & y_idx

            x[remove_idx] = np.nan
            y[remove_idx] = np.nan

    # Remove problem samples for individual session
    # In impossible locations for R068d8
    if info.session_id == "R068d8":
        for error_pt in info.path_pts["error"]:
            x_idx = np.abs(x - error_pt[0]) <= 20.0
            y_idx = np.abs(y - error_pt[1]) <= 20.0
            remove_idx = x_idx & y_idx

            x[remove_idx] = np.nan
            y[remove_idx] = np.nan

    # Remove idx when led is on and target is close to active feeder location
    x_idx = np.abs(x - feeder_x_location[..., np.newaxis]) <= dist_thresh
    y_idx = np.abs(y - feeder_y_location[..., np.newaxis]) <= dist_thresh
    remove_idx = x_idx & y_idx

    x[remove_idx] = np.nan
    y[remove_idx] = np.nan

    # Removing the problem samples that are furthest from the previous location
    def remove_based_on_std(original_targets, std_thresh=std_thresh):
        targets = np.array(original_targets)
        stds = np.nanstd(targets, axis=1)[:, np.newaxis]

        # find idx where there is a large variation between targets
        problem_samples = np.where(stds > std_thresh)[0]

        for i in problem_samples:
            # find the previous mean to help determine which target is an issue
            previous_idx = i - 1
            previous_mean = np.nanmean(targets[previous_idx])

            # if previous sample is nan, compare current sample to the one before that
            while np.isnan(previous_mean):
                previous_idx -= 1
                previous_mean = np.nanmean(targets[previous_idx])

            # remove problem target
            idx = np.nanargmax(np.abs(targets[i] - previous_mean))
            targets[i][idx] = np.nan

        return targets

    x = remove_based_on_std(x)
    y = remove_based_on_std(y)

    # Calculating the mean of the remaining targets
    x = np.nanmean(x, axis=1)
    y = np.nanmean(y, axis=1)

    # Interpolating for nan samples
    def interpolate(time, array, nan_idx):
        f = scipy.interpolate.interp1d(
            time[~nan_idx], array[~nan_idx], kind="linear", bounds_error=False
        )
        array[nan_idx] = f(time[nan_idx])

    xx = np.array(x)
    yy = np.array(y)
    ttimes = np.array(times)

    # Interpolate positions to replace nans during experiment phases
    for phase in meta.task_times:
        start = task_times[phase].start
        stop = task_times[phase].stop

        idx = (times >= start) & (times < stop)
        this_x = x[idx]
        this_y = y[idx]
        this_times = times[idx]

        # Finding nan idx
        x_nan_idx = np.isnan(this_x)
        y_nan_idx = np.isnan(this_y)
        nan_idx = x_nan_idx | y_nan_idx

        interpolate(this_times, this_x, nan_idx)
        interpolate(this_times, this_y, nan_idx)

        xx[idx] = this_x
        yy[idx] = this_y

    # Finding nan idx
    x_nan_idx = np.isnan(xx)
    y_nan_idx = np.isnan(yy)
    nan_idx = x_nan_idx | y_nan_idx

    # Removing nan idx
    xx = xx[~nan_idx]
    yy = yy[~nan_idx]
    ttimes = ttimes[~nan_idx]

    # Apply a median filter
    xx, yy = median_filter(xx, yy, kernel=11)

    # Construct a position object
    position = nept.Position(np.hstack(np.array([xx, yy])[..., np.newaxis]), ttimes)

    return position


@task(infos=meta_session.all_infos, cache_saves="events")
def cache_events(info):
    """Cache raw event data in .pkl"""
    events = nept.load_events(paths.event_file(info), meta.event_labels)
    if info.session_id == "R063d8":
        events["stop"] = np.insert(events["stop"], 3, 4158.9)
    elif info.session_id == "R066d1":
        events["start"] = events["start"][[0, 1, 289, 290, 291, 292, 293]]
        events["stop"] = events["stop"][[0, 1, 289, 290, 291, 292, 293]]
    elif info.session_id == "R066d6":
        events["stop"][1] -= 38.2
    elif info.session_id == "R067d1":
        events["start"] = np.delete(events["start"], [6, 7])
        events["stop"] = np.delete(events["stop"], [5, 6])
    elif info.session_id == "R067d6":
        events["stop"][3] = 3713.6752699999997
        events["start"][4] = 3727.656356
    elif info.session_id == "R068d8":
        events["start"][3] = 2348.339218
        events["stop"][3] = 3534.12544
        events["start"][5] = 5490.182978
    return events


@task(infos=meta_session.all_infos, cache_saves="task_times")
def cache_task_times(info, *, events, lfp_swr):
    assert (
        events["start"].size == 7 and events["stop"].size == 7
    ), f"{info.session_id} needs special treatment"

    task_times = {}
    for i, task_time in enumerate(meta.task_times):
        start = events["start"][i]
        start = lfp_swr.time[lfp_swr.time >= start][0]
        stop = events["stop"][i]
        stop = lfp_swr.time[lfp_swr.time <= stop][-1]
        task_times[task_time] = nept.Epoch([start], [stop])

    maze_times = nept.Epoch([], [])
    for run_time in meta.run_times:
        maze_times = maze_times.join(task_times[run_time])
    task_times["maze_times"] = maze_times

    pedestal_times = nept.Epoch([], [])
    for pedestal_time in meta.rest_times:
        pedestal_times = pedestal_times.join(task_times[pedestal_time])
    task_times["pedestal_times"] = pedestal_times

    task_times["all"] = maze_times.join(pedestal_times)

    for task_time in meta.task_times:
        assert task_times[task_time].n_epochs == 1

    return task_times


@task(infos=meta_session.all_infos, cache_saves="lfp_swr")
def cache_lfp_swr(info):
    """Cache raw lfp_swr data in .pkl"""
    lfp_swr = nept.load_lfp(paths.lfp_swr_file(info))
    # In one case, the last 3000 or so samples end up with time == 0
    lfp_swr = lfp_swr[lfp_swr.time > 0]
    return lfp_swr


@task(infos=meta_session.all_infos, cache_saves="lfp_theta")
def cache_lfp_theta(info):
    """Cache raw lfp_theta data in .pkl"""
    return nept.load_lfp(paths.lfp_theta_file(info))


@task(infos=meta_session.all_infos, cache_saves="spikes")
def cache_spikes(info, *, task_times):
    """Cache raw spike data in .pkl"""

    recording_dir = paths.recording_dir(info)
    spikes = nept.load_spikes(recording_dir, load_questionable=meta.load_questionable)

    # Remove neurons that have a rate greater than max_rate (5 Hz)
    session_length = sum(
        task_times[task_time].durations[0] for task_time in meta.task_times
    )
    spikes = [
        spiketrain
        for spiketrain in spikes
        if spiketrain.n_spikes / session_length < meta.max_rate
    ]

    # Remove neurons that have fewer than min_spikes spikes (100)
    return np.asarray(
        [spiketrain for spiketrain in spikes if spiketrain.n_spikes > meta.min_spikes]
    )


@task(infos=meta_session.all_infos, cache_saves="position")
def cache_position(info, *, events, task_times):
    """Cache raw position data in .pkl"""
    recording_dir = paths.recording_dir(info)

    unzip_nvt_file(recording_dir, f"{info.session}-VT1")
    position = load_shortcut_position(
        info, paths.position_file(info), events, task_times
    )
    os.remove(paths.position_file(info))

    # Save position as csv for ease of use in matlab
    csv = paths.position_csv_file(info)
    np.savetxt(
        csv,
        np.hstack(
            (
                position.x[:, np.newaxis],
                position.y[:, np.newaxis],
                position.time[:, np.newaxis],
            )
        ),
        delimiter=",",
        header="x,y,time",
        comments="",
    )
    print(f"Saved {csv}")

    return position


@task(infos=meta_session.all_infos, cache_saves=["lines", "zones"])
def cache_lines_zones(info):
    """Cache zones and zone lines in .pkl"""
    lines = {
        trajectory: LineString(info.trajectories[trajectory])
        for trajectory in info.trajectories
    }

    for trajectory in meta.trajectories:
        traj_coords = list(lines[trajectory].coords)

        feeder1_stop = lines[trajectory].interpolate(meta.expand_by * meta.feeder_scale)
        feeder1_center = np.array(info.path_pts["feeder1"])[..., np.newaxis]
        feeder1_start = feeder1_center - (feeder1_stop.xy - feeder1_center)
        feeder1_start = Point(*feeder1_start)
        feeder1_coords = list(feeder1_start.coords)

        feeder2_start = lines[trajectory].interpolate(
            -meta.expand_by * meta.feeder_scale
        )
        feeder2_center = np.array(info.path_pts["feeder2"])[..., np.newaxis]
        feeder2_stop = feeder2_center - (feeder2_start.xy - feeder2_center)
        feeder2_stop = Point(*feeder2_stop)
        feeder2_coords = list(feeder2_stop.coords)

        # Move points before feeder1_stop to feeder1
        traj_start = lines[trajectory].project(feeder1_stop)
        while lines[trajectory].project(Point(*traj_coords[0])) < traj_start:
            feeder1_coords.append(traj_coords.pop(0))
        feeder1_coords.append(list(feeder1_stop.coords)[0])
        traj_coords.insert(0, list(feeder1_stop.coords)[0])
        lines[f"{trajectory}_feeder1"] = LineString(feeder1_coords)

        traj_stop = lines[trajectory].project(feeder2_start)
        # Move points before feeder2_start to feeder2
        for i in range(len(traj_coords) - 1, 0, -1):
            if lines[trajectory].project(Point(*traj_coords[i])) > traj_stop:
                feeder2_coords.insert(0, traj_coords.pop(i))
            else:
                break
        feeder2_coords.insert(0, list(feeder2_start.coords)[0])
        traj_coords.append(list(feeder2_start.coords)[0])
        lines[f"{trajectory}_feeder2"] = LineString(feeder2_coords)
        lines[trajectory] = LineString(traj_coords)
        lines[f"{trajectory}_with_feeders"] = LineString(
            feeder1_coords + traj_coords + feeder2_coords
        )

    zones = {
        trajectory: lines[trajectory].buffer(meta.expand_by, cap_style=CAP_STYLE.flat)
        for trajectory in lines
    }
    zones["pedestal"] = Point(*info.path_pts["pedestal"]).buffer(
        meta.expand_by * meta.pedestal_scale
    )
    return {"lines": lines, "zones": zones}


@task(infos=meta_session.all_infos, cache_saves="lines_matched")
def cache_lines_matched(info, *, lines, raw_matched_linear):
    for trajectory in meta.trajectories:
        linear = raw_matched_linear[trajectory]
        start = lines[trajectory].interpolate(np.min(linear.x))
        end = lines[trajectory].interpolate(np.max(linear.x))
        line = LineString(info.trajectories[trajectory])

        traj_coords = list(line.coords)
        start_coords = list(start.coords)
        traj_start = lines[trajectory].project(start)
        while lines[trajectory].project(Point(*traj_coords[0])) < traj_start:
            start_coords.append(traj_coords.pop(0))
        start_coords.append(list(start.coords)[0])
        traj_coords.insert(0, list(start.coords)[0])
        matched_without_start = LineString(traj_coords)

        end_coords = list(end.coords)
        traj_coords = list(matched_without_start.coords)

        traj_stop = lines[trajectory].project(end)
        for i in range(len(traj_coords) - 1, 0, -1):
            if lines[trajectory].project(Point(*traj_coords[i])) > traj_stop:
                end_coords.insert(0, traj_coords.pop(i))
            else:
                break
        end_coords.insert(0, list(end.coords)[0])
        traj_coords.append(list(end.coords)[0])

        lines[f"matched_{trajectory}"] = LineString(traj_coords)
    return lines
