import scipy.signal as signal
import numpy as np

import nept


def convert_to_cm(path_pts, xy_conversion):
    for key in path_pts:
        path_pts[key][0] = path_pts[key][0] / xy_conversion[0]
        path_pts[key][1] = path_pts[key][1] / xy_conversion[1]
    return path_pts


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


def sort_led_locations(info, events, times):
    """Combines and sorts led1 and led2 events

    Parameters
    ----------
    info: module
    events: dict of nept.Epochs
    times: np.array

    Returns
    -------
    feeder_x_location: np.array
    feeder_y_location: np.array

    """
    leds = []
    leds.extend([(event, 'led1') for event in events['led1']])
    leds.extend([(event, 'led2') for event in events['led2']])
    sorted_leds = sorted(leds)

    # Get an array of feeder locations when that feeder is actively flashing
    feeder_x_location = np.zeros(times.shape[0])
    feeder_y_location = np.zeros(times.shape[0])

    feeder1_x = info.path_pts['feeder1'][0]
    feeder1_y = info.path_pts['feeder1'][1]
    feeder2_x = info.path_pts['feeder2'][0]
    feeder2_y = info.path_pts['feeder2'][1]

    last_label = ''

    for time, label in sorted_leds:
        if label == last_label:
            continue
        idx = nept.find_nearest_idx(times, time)
        x_location = feeder1_x if label == 'led1' else feeder2_x
        y_location = feeder1_y if label == 'led1' else feeder2_y

        feeder_x_location[idx:] = x_location
        feeder_y_location[idx:] = y_location

        last_label = label
    return feeder_x_location, feeder_y_location


def correct_targets(subset_x, subset_y, feeder_x, feeder_y, contamination_thresh=3):
    col_idx = (np.sum(subset_x == 0, axis=0) == subset_x.shape[0]) & (np.sum(subset_y == 0, axis=0) == subset_y.shape[0])
    subset_x = subset_x[:, ~col_idx]
    subset_y = subset_y[:, ~col_idx]

    x = np.array(subset_x[:, 0])
    y = np.array(subset_y[:, 0])

    # One target is contaminated when the distance between the targets is large
    target_x_var = np.var(subset_x, axis=1)
    target_y_var = np.var(subset_y, axis=1)

    # Contaminated samples are using the feeder LED instead of the implant LEDs
    contaminated_idx = (target_x_var > contamination_thresh) | (target_y_var > contamination_thresh)

    # Non contaminated implant LED samples with targets get averaged
    idx = ~contaminated_idx
    x[idx] = np.mean(subset_x[idx], axis=1)
    y[idx] = np.mean(subset_y[idx], axis=1)

    # For contaminated samples, we use the sample that is furthest from the feeder location
    feeder_x_dist = subset_x - feeder_x[..., np.newaxis]
    feeder_y_dist = subset_y - feeder_y[..., np.newaxis]
    feeder_dist = np.sqrt(feeder_x_dist ** 2 + feeder_y_dist ** 2)

    furthest_idx = np.argmax(feeder_dist, axis=1)

    idx = contaminated_idx
    x[idx] = subset_x[idx, furthest_idx[idx]]
    y[idx] = subset_y[idx, furthest_idx[idx]]

    return x, y


def remove_jumps_to_feeder(x, y, time, info, jump_thresh, dist_thresh):
    # Find those indices that have unnatural jumps in the position.
    # Remove jump points within to the feeder location.
    # Not including jumps due to jumps in time (eg. from stopping the recording).

    while True:
        jumps = np.append(np.array([0]), np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2))
        remove_idx = jumps > jump_thresh

        # time_jumps = np.append(np.diff(time) > time_thresh, np.array([False], dtype=bool))
        # remove_idx[time_jumps] = False

        dist_feeder1 = np.sqrt((x - info.path_pts['feeder1'][0]) ** 2 + (y - info.path_pts['feeder1'][1]) ** 2)
        dist_feeder2 = np.sqrt((x - info.path_pts['feeder2'][0]) ** 2 + (y - info.path_pts['feeder2'][1]) ** 2)
        dist_feeder = np.minimum(dist_feeder1, dist_feeder2)
        dist_jumps = dist_feeder > dist_thresh
        remove_idx[dist_jumps] = False

        if np.sum(remove_idx) > 0:
            x = x[~remove_idx]
            y = y[~remove_idx]
            time = time[~remove_idx]
        else:
            break

    return x, y, time


def median_filter(x, y, kernel=3):
    # Applying a median filter to the x and y positions

    x = signal.medfilt(x, kernel_size=kernel)
    y = signal.medfilt(y, kernel_size=kernel)

    return x, y


def load_shortcut_position(info, filename, events):
    """Loads and corrects shortcut position.

    Parameters
    ----------
    info: module
    filename: str
    events: dict

    Returns
    -------
    position: nept.Position

    """
    nvt_data = nept.load_nvt(filename)
    targets = nvt_data['targets']
    times = nvt_data['time']

    # Initialize x, y arrays
    x = np.zeros(targets.shape)
    y = np.zeros(targets.shape)
    # time = np.zeros(targets.shape)

    # X and Y are stored in a custom bitfield. See Neuralynx data file format documentation for details.
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

    # Remove columns with no target data
    col_idx = (np.sum(x == 0, axis=0) == x.shape[0]) & (np.sum(y == 0, axis=0) == y.shape[0])
    x = np.array(x[:, ~col_idx])
    y = np.array(y[:, ~col_idx])

    # Remove rows with no target data
    row_idx = (np.sum(x == 0, axis=1) == x.shape[1]) | (np.sum(y == 0, axis=1) == y.shape[1])
    x = np.array(x[~row_idx])
    y = np.array(y[~row_idx])
    times = np.array(times[~row_idx])

    x = x / info.scale_targets[0]
    y = y / info.scale_targets[1]

    feeder_x_location, feeder_y_location = sort_led_locations(info, events, times)

    # Initialize out_x and out_y as the first target
    out_x = np.array(x[:, 0])
    out_y = np.array(y[:, 0])

    # This correction method assumes we are working with two targets
    # (eg. subtracts the two targets, averages over two targets, etc.)
    if x.shape[1] == 1 and y.shape[1] == 1:
        # Remove jumps to feeder location
        out_x, out_y, times = remove_jumps_to_feeder(out_x, out_y, times, info, jump_thresh=20, dist_thresh=4)

        # Apply a median filter
        out_x, out_y = median_filter(out_x, out_y)

        position = nept.Position(np.hstack(np.array([out_x, out_y])[..., np.newaxis]), times)

        return position

    elif x.shape[1] == 2 and y.shape[1] == 2:
        # Find indices where only two targets were available
        two_target_idx = (x[:, 1] != 0) | (y[:, 1] != 0)
        subset_indices = [two_target_idx]

    elif x.shape[1] == 3 and y.shape[1] == 3:
        # Find indices where all three targets are available
        three_target_idx = (x[:, 2] != 0) | (y[:, 2] != 0)

        # Find indices where only two targets are available
        two_target_idx = ((x[:, 1] != 0) | (y[:, 1] != 0)) & ~three_target_idx
        subset_indices = [two_target_idx, three_target_idx]

    else:
        raise NotImplementedError(
            "this number of targets is not handled (%d x targets, %d y targets)" % (x.shape[1], y.shape[1]))

    for subset_idx in subset_indices:
        subset_x, subset_y = correct_targets(x[subset_idx], y[subset_idx],
                                             feeder_x_location[subset_idx], feeder_y_location[subset_idx])
        out_x[subset_idx] = subset_x
        out_y[subset_idx] = subset_y

    # Remove jumps to feeder location
    out_x, out_y, times = remove_jumps_to_feeder(out_x, out_y, times, info, jump_thresh=20, dist_thresh=4)

    # Apply a median filter
    out_x, out_y = median_filter(out_x, out_y)

    # Construct a nept.Position object
    position = nept.Position(np.hstack(np.array([out_x, out_y])[..., np.newaxis]), times)

    return position


def load_shortcut_pos(info, filename, events, variance_thresh=4., epsilon=0.01):
    """Loads and corrects shortcut position.

    Parameters
    ----------
    info: module
    filename: str
    events: dict
    variance_thresh: float
    epsilon: float

    Returns
    -------
    position: nept.Position

    """
    # Load raw position from file
    nvt_data = nept.load_nvt(filename)
    targets = nvt_data['targets']
    times = nvt_data['time']

    # Initialize x, y arrays
    x = np.zeros(targets.shape)
    y = np.zeros(targets.shape)

    # X and Y are stored in a custom bitfield. See Neuralynx data file format documentation for details.
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
    x = x / info.scale_targets[0]
    y = y / info.scale_targets[1]

    # Finding which feeder led is on over time
    leds = []
    leds.extend([(event, 'led1') for event in events['led1']])
    leds.extend([(event, 'led2') for event in events['led2']])
    sorted_leds = sorted(leds)

    # Get an array of feeder locations when that feeder is actively flashing
    feeder_x_location = np.empty(times.shape[0]) * np.nan
    feeder_y_location = np.empty(times.shape[0]) * np.nan

    n_ledon = 6
    for time, label in sorted_leds:
        idx = nept.find_nearest_idx(times, time)
        x_location = info.path_pts['feeder1'][0] if label == 'led1' else info.path_pts['feeder2'][0]
        y_location = info.path_pts['feeder1'][1] if label == 'led1' else info.path_pts['feeder2'][1]

        feeder_x_location[idx:idx + n_ledon] = x_location
        feeder_y_location[idx:idx + n_ledon] = y_location

    # Removing the contaminated samples that are closest to the feeder location
    def remove_feeder_contamination(original_targets, current_feeder, dist_to_feeder=5):
        targets = np.array(original_targets)
        for i, (target, feeder) in enumerate(zip(targets, current_feeder)):
            if not np.isnan(feeder):
                dist = np.abs(target - feeder) < dist_to_feeder
                target[dist] = np.nan
            targets[i] = target
        return targets

    x = remove_feeder_contamination(x, feeder_x_location)
    y = remove_feeder_contamination(y, feeder_y_location)

    # Removing the problem samples that are furthest from the previous location
    def remove_based_on_std(original_targets, std_thresh=10):
        targets = np.array(original_targets)
        stds = np.nanstd(targets, axis=1)[:, np.newaxis]

        # find idx where there is a large variation between targets
        problem_samples = np.where(stds > std_thresh)[0]

        for i in problem_samples:
            # find the previous mean to help determine which target is an issue
            previous_idx = i-1
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
    xx = np.nanmean(x, axis=1)
    yy = np.nanmean(y, axis=1)
    ttimes = times

    # Apply a median filter
    xx, yy = median_filter(xx, yy)

    return nept.Position(np.hstack(np.array([xx, yy])[..., np.newaxis]), ttimes)
