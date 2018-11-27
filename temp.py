import matplotlib.pyplot as plt
import os
import numpy as np
import nept

from loading_data import get_data

import info.r068d5 as info
events, position, spikes, lfp, lfp_theta = get_data(info)

thisdir = os.path.dirname(os.path.realpath(__file__))
output_filepath = os.path.join(thisdir, "plots", "check-prerecord")
if not os.path.exists(output_filepath):
    os.makedirs(output_filepath)

start = info.task_times["prerecord"].start
stop = info.task_times["prerecord"].stop

# parameters
z_thresh = 1
merge_thresh = 0.01
min_length = 0.03
fs = info.fs
thresh = (140.0, 250.0)
min_involved = 4

rest_labels = ["prerecord", "pauseA", "pauseB", "postrecord"]
rest_starts = [info.task_times[task_label].start for task_label in rest_labels]
rest_stops = [info.task_times[task_label].stop for task_label in rest_labels]
rest_lfp = lfp.time_slice(rest_starts, rest_stops)

swrs = nept.detect_swr_hilbert(rest_lfp, fs, thresh, z_thresh, merge_thresh=merge_thresh, min_length=min_length)
swrs = nept.find_multi_in_epochs(spikes, swrs, min_involved=min_involved)

swrs = swrs.time_slice(start, stop)

print(swrs.n_epochs)
sliced_lfp = lfp.time_slice(start, stop)

all_spikes = np.sort(np.concatenate([spiketrain.time for spiketrain in spikes]))
sliced_all_spikes = all_spikes[(start <= all_spikes) & (all_spikes <= stop)]

dt = 0.02
std = 0.01
firing_thresh = 20
bin_edges = nept.get_edges(sliced_all_spikes, dt)

convolved_spikes = np.histogram(sliced_all_spikes, bins=bin_edges)[0].astype(float)
convolved_spikes = nept.gaussian_filter(convolved_spikes, std=std, dt=dt)

# # Finding locations where the firing rate is above thresh
# detect = convolved_spikes > firing_thresh
# detect = np.hstack([0, detect, 0])  # pad to detect first or last element change
# signal_change = np.diff(detect.astype(int))
#
# start_idx = np.where(signal_change == 1)[0]
# stop_idx = np.where(signal_change == -1)[0] - 1
#
# high_firing_rates = nept.Epoch([lfp.time[start_idx], lfp.time[stop_idx]])

fig, ax = plt.subplots()
plt.plot(sliced_lfp.time, sliced_lfp.data)
plt.plot(sliced_all_spikes, np.ones(len(sliced_all_spikes))*0.0002, ".")
plt.plot(bin_edges[:-1], convolved_spikes/(50*2000)+0.00025)
for start, stop in zip(swrs.starts, swrs.stops):
    this_swr_lfp = lfp.time_slice(start, stop)
    plt.plot(this_swr_lfp.time, this_swr_lfp.data, "r")
plt.text(0.01, 0.01, "n_swrs: " + str(swrs.n_epochs), transform=ax.transAxes)
# for start, stop in zip(high_firing_rates.starts, high_firing_rates.stops):
#     ax.fill_between((start, stop), 50, color="k", alpha=0.1)
plt.show()
# plt.savefig(os.path.join(output_filepath, info.session_id+"_check-swr-prerecord_zthresh"+str(z_thresh)+".png"))
# plt.close()
