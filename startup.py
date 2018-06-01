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


def median_filter(x, y, kernel=3):
    # Applying a median filter to the x and y positions

    x = signal.medfilt(x, kernel_size=kernel)
    y = signal.medfilt(y, kernel_size=kernel)

    return x, y


def load_shortcut_position(info, filename, events, n_ledon=6, dist_to_feeder=5, std_thresh=10.):
    """Loads and corrects shortcut position.

    Parameters
    ----------
    info: module
    filename: str
    events: dict
    n_ledon: int
    dist_to_feeder: int
    std_thresh: float

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

    for time, label in sorted_leds:
        idx = nept.find_nearest_idx(times, time)
        x_location = info.path_pts['feeder1'][0] if label == 'led1' else info.path_pts['feeder2'][0]
        y_location = info.path_pts['feeder1'][1] if label == 'led1' else info.path_pts['feeder2'][1]

        feeder_x_location[idx:idx + n_ledon] = x_location
        feeder_y_location[idx:idx + n_ledon] = y_location

    # Removing the contaminated samples that are closest to the feeder location
    def remove_feeder_contamination(original_targets, current_feeder, dist_to_feeder=dist_to_feeder):
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
    def remove_based_on_std(original_targets, std_thresh=std_thresh):
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

    # Applying a median filter
    xx, yy = median_filter(xx, yy)

    # Finding nan idx
    x_nan_idx = np.isnan(xx)
    y_nan_idx = np.isnan(yy)
    nan_idx = x_nan_idx | y_nan_idx

    # Removing nan samples
    xx = xx[~nan_idx]
    yy = yy[~nan_idx]
    ttimes = ttimes[~nan_idx]

    return nept.Position(np.hstack(np.array([xx, yy])[..., np.newaxis]), ttimes)
