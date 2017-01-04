import os
import numpy as np
import pickle

import vdmlab as vdm

from loading_data import get_data
from utils_fields import get_unique_fields, categorize_fields
from utils_maze import find_zones

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')


def analyze(info, tuning_curve, experiment_time, all_tracks_tc=False):
    print('cooccur:', info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= 0.1
    run_pos = position[run_idx]

    track_starts = [info.task_times['phase1'].start,
                    info.task_times['phase2'].start,
                    info.task_times['phase3'].start]
    track_stops = [info.task_times['phase1'].stop,
                   info.task_times['phase2'].stop,
                   info.task_times['phase3'].stop]

    track_pos = run_pos.time_slices(track_starts, track_stops)

    binsize = 3
    xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
    yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)

    zones = find_zones(info)

    field_thresh = 1.0
    fields_tunings = categorize_fields(tuning_curve, zones, xedges, yedges, field_thresh=field_thresh)

    unique_fields = dict()
    unique_fields['u'] = get_unique_fields(fields_tunings['u'],
                                           fields_tunings['shortcut'],
                                           fields_tunings['novel'])
    unique_fields['shortcut'] = get_unique_fields(fields_tunings['shortcut'],
                                                  fields_tunings['novel'],
                                                  fields_tunings['u'])
    unique_fields['novel'] = get_unique_fields(fields_tunings['novel'],
                                               fields_tunings['u'],
                                               fields_tunings['shortcut'])

    field_spikes = dict(u=[], shortcut=[], novel=[])
    for field in unique_fields.keys():
        for key in unique_fields[field]:
            field_spikes[field].append(spikes[key])

    t_start = info.task_times[experiment_time].start
    t_stop = info.task_times[experiment_time].stop

    sliced_lfp = lfp.time_slice(t_start, t_stop)

    sliced_spikes = [spiketrain.time_slice(t_start, t_stop) for spiketrain in spikes]

    z_thresh = 3.0
    power_thresh = 5.0
    merge_thresh = 0.02
    min_length = 0.01
    swrs = vdm.detect_swr_hilbert(sliced_lfp, fs=info.fs, thresh=(140.0, 250.0), z_thresh=z_thresh,
                                  power_thresh=power_thresh, merge_thresh=merge_thresh, min_length=min_length)

    multi_swrs = vdm.find_multi_in_epochs(sliced_spikes, swrs, min_involved=3)

    count_matrix = dict()
    for key in field_spikes:
        count_matrix[key] = vdm.spike_counts(field_spikes[key], multi_swrs)

    tetrode_mask = dict()
    for key in field_spikes:
        tetrode_mask[key] = vdm.get_tetrode_mask(field_spikes[key])

    probs = dict()
    for key in count_matrix:
        probs[key] = vdm.compute_cooccur(count_matrix[key], tetrode_mask[key], num_shuffles=10000)

    output = dict()
    output['probs'] = probs
    output['n_epochs'] = multi_swrs.n_epochs

    if all_tracks_tc:
        cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '_all-tracks.pkl'
    else:
        cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '.pkl'
    pickled_path = os.path.join(pickle_filepath, cooccur_filename)

    with open(pickled_path, 'wb') as fileobj:
        pickle.dump(output, fileobj)

    return output


if __name__ == "__main__":
    from run import spike_sorted_infos
    infos = spike_sorted_infos

    all_tracks_tc = True

    experiment_times = ['prerecord', 'postrecord', 'pauseA', 'pauseB']
    for experiment_time in experiment_times:
        print(experiment_time)
        for info in infos:
            if all_tracks_tc:
                tuning_curve_filename = info.session_id + '_tuning-curve_all-phases.pkl'
            else:
                tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
            pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
            with open(pickled_tuning_curve, 'rb') as fileobj:
                tuning_curve = pickle.load(fileobj)
            analyze(info, tuning_curve, experiment_time, all_tracks_tc)
