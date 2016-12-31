import os
# import scipy.io as sio
import scipy.signal as signal
import numpy as np

import vdmlab as vdm


def convert_to_cm(path_pts, xy_conversion):
    for key in path_pts:
        path_pts[key][0] = path_pts[key][0] / xy_conversion[0]
        path_pts[key][1] = path_pts[key][1] / xy_conversion[1]
    return path_pts


def load_data(info):
    thisdir = os.path.dirname(os.path.realpath(__file__))
    dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))

    events = vdm.load_events(os.path.join(dataloc, info.event_filename), info.event_labels)

    position = load_shortcut_position(info, os.path.join(dataloc, info.position_filename), events)

    spikes = vdm.load_spikes(os.path.join(dataloc, info.spikes_filepath))

    lfp_swr = vdm.load_lfp(os.path.join(dataloc, info.lfp_swr_filename))

    lfp_theta = vdm.load_lfp(os.path.join(dataloc, info.lfp_theta_filename))

    return events, position, spikes, lfp_swr, lfp_theta


def extract_xy(target, info):
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
    x = int(binary_target[20:31], 2) / info.pxl_to_cm[0]
    y = int(binary_target[4:15], 2) / info.pxl_to_cm[1]

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
    position: vdm.Position

    """
    nvt_data = vdm.load_nvt(filename)
    targets = nvt_data['targets']
    times = nvt_data['time']

    # Initialize x, y arrays
    x = np.zeros(targets.shape)
    y = np.zeros(targets.shape)
    # time = np.zeros(targets.shape)

    # X and Y are stored in a custom bitfield. See Neuralynx data file format documentation for details.
    # Briefly, each record contains up to 50 targets, each stored in 32bit field.
    # X field at [20:31] and Y at [4:15].
    for target in range(targets.shape[1]):
        this_sample = targets[:, target]
        for sample in range(targets.shape[0]):
            # When the bitfield is equal to zero there is no valid data for that field
            # and remains zero for the rest of the bitfields in the record.
            if this_sample[target] == 0:
                break
            x[sample, target], y[sample, target] = extract_xy(int(this_sample[sample]), info)

    # Remove columns with no target data
    col_idx = (np.sum(x == 0, axis=0) == x.shape[0]) & (np.sum(y == 0, axis=0) == y.shape[0])
    xs = np.array(x[:, ~col_idx])
    ys = np.array(y[:, ~col_idx])

    # This correction method assumes we are working with two targets
    # (eg. subtracts the two targets, averages over two targets, etc.)
    if xs.shape[1] != 2 or ys.shape[1] != 2:
        raise ValueError("must have two targets for x and y")

    # Put the LED events in the same array, sorted by time
    leds = []
    leds.extend([(event, 'led1') for event in events['led1']])
    leds.extend([(event, 'led2') for event in events['led2']])
    sorted_leds = sorted(leds)

    # Get an array of feeder locations when that feeder is actively flashing
    feeder_x_location = np.zeros(xs.shape[0])
    feeder_y_location = np.zeros(ys.shape[0])

    feeder1_x = info.path_pts['feeder1'][0]
    feeder1_y = info.path_pts['feeder1'][1]
    feeder2_x = info.path_pts['feeder2'][0]
    feeder2_y = info.path_pts['feeder2'][1]

    last_label = ''

    for time, label in sorted_leds:
        if label == last_label:
            continue
        idx = vdm.find_nearest_idx(times, time)
        x_location = feeder1_x if label == 'led1' else feeder2_x
        y_location = feeder1_y if label == 'led1' else feeder2_y

        feeder_x_location[idx:] = x_location
        feeder_y_location[idx:] = y_location

        last_label = label

    # Initialize xx and yy as the first target
    xx = np.array(xs[:, 0])
    yy = np.array(ys[:, 0])

    # Find indices where only one target was available
    one_target_idx = (xs[:, 1] == 0) | (ys[:, 1] == 0)

    # One target is contaminated when the distance between the two targets is large
    target_x_dist = np.abs(xs[:, 1] - xs[:, 0])
    target_y_dist = np.abs(ys[:, 1] - ys[:, 0])

    # Contaminated samples are using the feeder LED instead of the implant LEDs
    contamination_thresh = 5
    contaminated_idx = (target_x_dist > contamination_thresh) | (target_y_dist > contamination_thresh)

    # Non contaminated implant LED samples with two targets get averaged
    idx = ~contaminated_idx & ~one_target_idx
    xx[idx] = np.mean(xs[idx], axis=1)
    yy[idx] = np.mean(ys[idx], axis=1)

    # For contaminated samples, we use the sample that is furthest from the feeder location
    feeder_x_dist = np.abs(xs - feeder_x_location[..., np.newaxis])
    feeder_y_dist = np.abs(ys - feeder_y_location[..., np.newaxis])

    feeder_dist = feeder_x_dist + feeder_y_dist
    furthest_idx = np.argmax(feeder_dist, axis=1)

    idx = contaminated_idx & ~one_target_idx
    xx[idx] = xs[idx, furthest_idx[idx]]
    yy[idx] = ys[idx, furthest_idx[idx]]

    # Applying a median filter to the x and y positions
    kernel = 3
    filtered_x = signal.medfilt(xx, kernel_size=kernel)
    filtered_y = signal.medfilt(yy, kernel_size=kernel)

    # Construct a vdm.Position object
    position = vdm.Position(np.hstack(np.array([filtered_x, filtered_y])[..., np.newaxis]), times)

    return position
