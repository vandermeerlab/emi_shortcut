import os
import pickle
import zipfile
import warnings
import nept

import matplotlib.pyplot as plt

from startup import load_shortcut_position, load_shortcut_pos

warnings.filterwarnings("ignore")


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


def load_data(info):
    thisdir = os.path.dirname(os.path.realpath(__file__))
    dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))

    events = nept.load_events(os.path.join(dataloc, info.event_filename), info.event_labels)

    position_path = os.path.join(dataloc, 'data-working', info.rat_id, info.session+'_recording')
    unzip_nvt_file(position_path, info.session+'-VT1', info)
    position = load_shortcut_pos(info, os.path.join(dataloc, info.position_filename), events)
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

    spikes_path = os.path.join(dataloc, info.pickled_spikes)
    with open(spikes_path, 'wb') as fileobj:
        pickle.dump(spikes, fileobj)

    lfp_swr_path = os.path.join(dataloc, info.pickled_lfp_swr)
    with open(lfp_swr_path, 'wb') as fileobj:
        pickle.dump(lfp_swr, fileobj)

    lfp_theta_path = os.path.join(dataloc, info.pickled_lfp_theta)
    with open(lfp_theta_path, 'wb') as fileobj:
        pickle.dump(lfp_theta, fileobj)


def get_data(info):
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
        events, position, spikes, lfp_swr, lfp_theta = load_data(info)

    return events, position, spikes, lfp_swr, lfp_theta


if __name__ == "__main__":
    from run import spike_sorted_infos, info, r067_infos
    infos = spike_sorted_infos
    # infos = [info.r063d8]
    # infos = r067_infos

    for info in infos:
        print(info.session_id)
        # save_data(info)
        # events, position, spikes, lfp_swr, lfp_theta = get_data(info)
        events, position, spikes, lfp_swr, lfp_theta = load_data(info)



        thisdir = os.getcwd()
        dataloc = os.path.join(thisdir, 'cache', 'data')
        pickle_filepath = os.path.join(thisdir, "cache", "pickled")
        output_filepath = os.path.join(thisdir, "plots", "correcting_position")

        # plot to check
        fig, ax = plt.subplots()
        plt.plot(position.time, position.y, "k.", ms=3)
        plt.xlabel("time")
        plt.ylabel("y")
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        plt.title("n_samples:" + str(position.n_samples))
        plt.tight_layout()
        plt.savefig(os.path.join(output_filepath, info.session_id+"_corrected-position_new_y.png"))
        # plt.show()
