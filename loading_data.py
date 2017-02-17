import os
import pickle
import nept

from startup import load_shortcut_position


def load_data(info):
    thisdir = os.path.dirname(os.path.realpath(__file__))
    dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))

    events = nept.load_events(os.path.join(dataloc, info.event_filename), info.event_labels)

    position = load_shortcut_position(info, os.path.join(dataloc, info.position_filename), events)

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
    from run import spike_sorted_infos, info
    infos = spike_sorted_infos
    # infos = [info.r066d3]

    for info in infos:
        print(info.session_id)
        save_data(info)
        # events, position, spikes, lfp_swr, lfp_theta = get_data(info)
