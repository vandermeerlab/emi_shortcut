import os
import numpy as np
import pickle

import vdmlab as vdm

from load_data import get_pos, get_spikes, get_lfp
from analyze_fields import get_unique_fields, categorize_fields
from analyze_maze import find_zones

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'cooccur')


def analyze(info, tuning_curve, experiment_time):
    print('cooccur:', info.session_id)

    lfp = get_lfp(info.good_swr[0])
    position = get_pos(info.pos_mat, info.pxl_to_cm)
    spikes = get_spikes(info.spike_mat)

    speed = position.speed(t_smooth=0.5)
    run_idx = np.squeeze(speed.data) >= 0.1
    run_pos = position[run_idx]

    t_start_tc = info.task_times['phase3'].start
    t_stop_tc = info.task_times['phase3'].stop

    tc_pos = run_pos.time_slice(t_start_tc, t_stop_tc)

    binsize = 3
    xedges = np.arange(tc_pos.x.min(), tc_pos.x.max() + binsize, binsize)
    yedges = np.arange(tc_pos.y.min(), tc_pos.y.max() + binsize, binsize)

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

    cooccur_filename = info.session_id + '_cooccur-' + experiment_time + '.pkl'
    pickled_path = os.path.join(pickle_filepath, cooccur_filename)

    with open(pickled_path, 'wb') as fileobj:
        pickle.dump(output, fileobj)

    return output


if __name__ == "__main__":
    from run import test
    infos = test

    if 1:
        experiment_time = 'pauseA'
        for info in infos:
            tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
            pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
            with open(pickled_tuning_curve, 'rb') as fileobj:
                tuning_curve = pickle.load(fileobj)

            analyze(info, tuning_curve, experiment_time)

    if 0:
        experiment_time = 'pauseB'
        for info in infos:
            tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
            pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
            with open(pickled_tuning_curve, 'rb') as fileobj:
                tuning_curve = pickle.load(fileobj)

            analyze(info, tuning_curve, experiment_time)
