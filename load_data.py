import os

from startup import load_csc, load_videotrack, load_events, load_spikes


thisdir = os.path.dirname(os.path.realpath(__file__))
dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))


def get_csc(lfp_mat):
    return load_csc(os.path.join(dataloc, lfp_mat))


def get_pos(pos_mat, pxl_to_cm):
    pos = load_videotrack(os.path.join(dataloc, pos_mat))
    pos['x'] = pos['x'] / pxl_to_cm[0]
    pos['y'] = pos['y'] / pxl_to_cm[1]
    return pos


def get_events(event_mat):
    return load_events(os.path.join(dataloc, event_mat))


def get_spikes(spike_mat):
    return load_spikes(os.path.join(dataloc, spike_mat))
