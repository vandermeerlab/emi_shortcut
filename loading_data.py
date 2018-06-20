import os
import numpy as np
import scipy
import pickle
import zipfile
import warnings
import nept

import matplotlib.pyplot as plt

from utils_maze import get_trials

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
    file = zipfile.ZipFile(os.path.join(datapath, filename+'.zip'), 'w')
    file.write(os.path.join(datapath, filename+'.nvt'), filename+'.nvt',
               compress_type=zipfile.ZIP_DEFLATED)

    file.close()


def unzip_nvt_file(datapath, filename, info):
    """Extracts a videotracking (*.nvt) file

    Parameters
    ----------
    datapath: str
    filename: str

    """
    with zipfile.ZipFile(os.path.join(datapath, filename+'.zip'), 'r') as file:
        file.extractall(datapath)

    # os.rename(os.path.join(datapath, 'VT1.nvt'), os.path.join(datapath, info.session+'-VT1.nvt'))

    file.close()


def load_shortcut_position(info, filename, events, with_interpolation,
                           dist_thresh=20., std_thresh=2., output_filepath=None):
    """Loads and corrects shortcut position.

    Parameters
    ----------
    info: module
    filename: str
    events: dict
    dist_thresh: float
    std_thresh: float
    output_filepath: str

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
    x /= info.scale_targets
    y /= info.scale_targets

    off_delay = np.median(np.diff(times))

    # Finding which feeder led is on over time
    leds = []
    leds.extend([(event, 'led1') for event in events['led1']])
    leds.extend([(event, 'led2') for event in events['led2']])
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

        x_location = info.path_pts['feeder1'][0] if label == 'led2' else info.path_pts['feeder2'][0]
        y_location = info.path_pts['feeder1'][1] if label == 'led2' else info.path_pts['feeder2'][1]

        feeder_x_location[np.logical_and(times >= start - off_delay, times < ledoff[off_idx] + off_delay)] = x_location
        feeder_y_location[np.logical_and(times >= start - off_delay, times < ledoff[off_idx] + off_delay)] = y_location

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
        f = scipy.interpolate.interp1d(time[~nan_idx], array[~nan_idx], kind='linear', bounds_error=False)
        array[nan_idx] = f(time[nan_idx])

    xx = np.array(x)
    yy = np.array(y)
    ttimes = np.array(times)

    if with_interpolation:
        maze_phases = ["phase1", "phase2", "phase3"]
        for task_time in info.task_times.keys():
            # Interpolate positions to replace nans during maze phases
            if task_time in maze_phases:
                trial_epochs = get_trials(events, info.task_times[task_time])
                for start, stop in zip(trial_epochs.starts, trial_epochs.stops):
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

    if output_filepath is not None:
        plot_correcting_position(info, position, targets, events, output_filepath, with_interpolation)

    return position


def load_data(info, output_path=None):
    thisdir = os.path.dirname(os.path.realpath(__file__))
    dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))

    events = nept.load_events(os.path.join(dataloc, info.event_filename), info.event_labels)

    position_path = os.path.join(dataloc, 'data-working', info.rat_id, info.session+'_recording')
    unzip_nvt_file(position_path, info.session+'-VT1', info)
    for with_interpolation in [True, False]:
        position = load_shortcut_position(info, os.path.join(dataloc, info.position_filename), events,
                                          with_interpolation=with_interpolation,
                                          output_filepath=output_path)
    os.remove(os.path.join(position_path, info.session+'-VT1.nvt'))

    spikes = nept.load_spikes(os.path.join(dataloc, info.spikes_filepath))

    lfp_swr = nept.load_lfp(os.path.join(dataloc, info.lfp_swr_filename))

    lfp_theta = nept.load_lfp(os.path.join(dataloc, info.lfp_theta_filename))

    return events, position, spikes, lfp_swr, lfp_theta


def save_data(info):
    thisdir = os.path.dirname(os.path.realpath(__file__))
    dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))

    events, position, spikes, lfp_swr, lfp_theta = load_data(info)

    events_path = os.path.join(dataloc, info.pickled_events)
    with open(events_path, 'wb') as fileobj:
        pickle.dump(events, fileobj)

    position_path = os.path.join(dataloc, info.pickled_position)
    with open(position_path, 'wb') as fileobj:
        pickle.dump(position, fileobj)

    # Also save position as csv for ease of use in matlab
    filename = os.path.join(dataloc, info.session_id + "-position.csv")
    np.savetxt(filename,
               np.hstack((position.x[:, np.newaxis], position.y[:, np.newaxis], position.time[:, np.newaxis])),
               delimiter=",", header="x,y,time", comments="")

    spikes_path = os.path.join(dataloc, info.pickled_spikes)
    with open(spikes_path, 'wb') as fileobj:
        pickle.dump(spikes, fileobj)

    lfp_swr_path = os.path.join(dataloc, info.pickled_lfp_swr)
    with open(lfp_swr_path, 'wb') as fileobj:
        pickle.dump(lfp_swr, fileobj)

    lfp_theta_path = os.path.join(dataloc, info.pickled_lfp_theta)
    with open(lfp_theta_path, 'wb') as fileobj:
        pickle.dump(lfp_theta, fileobj)


def get_data(info, output_path=None):
    """Gets data from pickled file if available or loads from Neuralynx data files

    Parameters
    ----------
    info: module

    Returns
    -------
    events: dict of nept.Epoch
    position: nept.Position
    spikes: list of nept.SpikeTrains
    lfp_swr: nept.AnalogSignal
    lfp_theta: nept.AnalogSignal

    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))

    events_path = os.path.join(dataloc, info.pickled_events)
    position_path = os.path.join(dataloc, info.pickled_position)
    spikes_path = os.path.join(dataloc, info.pickled_spikes)
    lfp_swr_path = os.path.join(dataloc, info.pickled_lfp_swr)
    lfp_theta_path = os.path.join(dataloc, info.pickled_lfp_theta)

    if os.path.exists(events_path):
        with open(events_path, 'rb') as fileobj:
            events = pickle.load(fileobj)
        with open(position_path, 'rb') as fileobj:
            position = pickle.load(fileobj)
        with open(spikes_path, 'rb') as fileobj:
            spikes = pickle.load(fileobj)
        with open(lfp_swr_path, 'rb') as fileobj:
            lfp_swr = pickle.load(fileobj)
        with open(lfp_theta_path, 'rb') as fileobj:
            lfp_theta = pickle.load(fileobj)
    else:
        events, position, spikes, lfp_swr, lfp_theta = load_data(info, output_path)

    return events, position, spikes, lfp_swr, lfp_theta


def plot_trials(info, position, events, savepath):
    for phase in ["phase1", "phase2", "phase3"]:
        trial_epochs = get_trials(events, info.task_times[phase])
        for trial_idx in range(trial_epochs.n_epochs):
            start = trial_epochs[trial_idx].start
            stop = trial_epochs[trial_idx].stop

            trial = position.time_slice(start, stop)
            plt.plot(trial.time, trial.y, "k.")
            title = info.session_id + " " + phase + " trial" + str(trial_idx)
            plt.title(title)
            if savepath is not None:
                plt.savefig(os.path.join(savepath, "trials", title))
                plt.close()
            else:
                plt.show()
                plt.close()


def plot_correcting_position(info, position, targets, events, savepath=None, with_interpolation=True):
    fig = plt.figure(figsize=(8, 8))

    fig.suptitle(info.session_id, y=1.)

    ax1 = plt.subplot(321)
    ax1 = plt.plot(position.x, position.y, "k.", ms=5)

    trial_epochs = get_trials(events, info.task_times["phase3"])
    trial_idx = 3
    start = trial_epochs[trial_idx].start
    stop = trial_epochs[trial_idx].stop
    trial = position.time_slice(start, stop)
    ax2 = plt.subplot(322)
    ax2 = plt.plot(trial.x, trial.y, "g.", ms=5)

    ax3 = plt.subplot(312)
    ax3 = plt.plot(position.time, position.y, "b.", ms=5)

    start_idx = nept.find_nearest_idx(position.time, info.task_times["phase3"].start)
    n_idx = 10000
    stop_idx = start_idx + n_idx
    ax4 = plt.subplot(313)
    ax4 = plt.plot(position.time[start_idx:stop_idx], position.y[start_idx:stop_idx], "r.", ms=5)

    plt.text(position.time[stop_idx]-20, -50, str(round(position.n_samples / len(targets) * 100, 2))+"%")

    # Cleaning up the plot
    plt.tight_layout()

    if savepath:
        if with_interpolation:
            filename = info.session_id+"-interpolated-correcting_position.png"
        else:
            filename = info.session_id+"-correcting_position.png"
        plt.savefig(os.path.join(savepath, filename))
        plt.close()
    else:
        plt.show()
        plt.close()

    plot_trials(info, position, events, savepath)


if __name__ == "__main__":
    from run import spike_sorted_infos, r063_infos, r066_infos, r067_infos, r068_infos
    infos = r068_infos

    for info in infos:
        print(info.session_id)
        save_data(info)
        # events, position, spikes, lfp_swr, lfp_theta = get_data(info)

        thisdir = os.getcwd()
        output_path = os.path.join(thisdir, "plots", "correcting_position")

        events, position, _, _, _ = load_data(info, output_path)



        # thisdir = os.getcwd()
        # dataloc = os.path.join(thisdir, 'cache', 'data')
        # pickle_filepath = os.path.join(thisdir, "cache", "pickled")
        # output_filepath = os.path.join(thisdir, "plots", "correcting_position")
        #
        # # plot to check
        # fig, ax = plt.subplots()
        # plt.plot(position.time, position.y, "k.", ms=3)
        # plt.xlabel("time")
        # plt.ylabel("y")
        # ax.spines['right'].set_visible(False)
        # ax.spines['top'].set_visible(False)
        # ax.yaxis.set_ticks_position('left')
        # ax.xaxis.set_ticks_position('bottom')
        # plt.title("n_samples:" + str(position.n_samples))
        # plt.tight_layout()
        # plt.savefig(os.path.join(output_filepath, info.session_id+"_corrected-position_new_y.png"))
        # # plt.show()
