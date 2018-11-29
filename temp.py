import matplotlib.pyplot as plt
import os
import numpy as np
import scipy
import nept

from loading_data import get_data

import info.r063d5 as info
events, position, spikes, lfp, lfp_theta = get_data(info)

thisdir = os.path.dirname(os.path.realpath(__file__))
output_filepath = os.path.join(thisdir, "plots", "check-prerecord")
if not os.path.exists(output_filepath):
    os.makedirs(output_filepath)

prerecord_start = info.task_times["prerecord"].start
prerecord_stop = info.task_times["prerecord"].stop

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

swrs = swrs.time_slice(prerecord_start, prerecord_stop)

print("n_swrs before mua thresh:", swrs.n_epochs)
sliced_lfp = lfp.time_slice(prerecord_start, prerecord_stop)

all_spikes = np.sort(np.concatenate([spiketrain.time for spiketrain in spikes]))

dt = 0.02
std = 0.01
bin_edges = nept.get_edges(sliced_lfp.time, dt)

convolved_spikes = np.histogram(all_spikes, bins=bin_edges)[0].astype(float)
convolved_spikes = nept.gaussian_filter(convolved_spikes, std=std, dt=dt)

z_spikes_thresh = 2
multi_unit = nept.get_epoch_from_zscored_thresh(convolved_spikes, bin_edges, thresh=z_spikes_thresh)

#for plotting
sliced_all_spikes = all_spikes[(prerecord_start <= all_spikes) & (all_spikes <= prerecord_stop)]
zscored = scipy.stats.zscore(convolved_spikes)
zthresh_idx = (np.abs(zscored - z_spikes_thresh)).argmin()
raw_thresh = convolved_spikes[zthresh_idx]

these_swrs = multi_unit.overlaps(swrs)
print("n_swrs after mua thresh:", these_swrs.n_epochs)

fig, ax = plt.subplots()
plt.plot(bin_edges[:-1], convolved_spikes/(50*2000)+0.00025, "g")
plt.axhline(raw_thresh/(50*2000)+0.00025, color="k")
plt.plot(sliced_lfp.time, sliced_lfp.data)
plt.plot(sliced_all_spikes, np.ones(len(sliced_all_spikes))*0.0002, ".")
for start, stop in zip(swrs.starts, swrs.stops):
    this_swr_lfp = lfp.time_slice(start, stop)
    plt.plot(this_swr_lfp.time, this_swr_lfp.data, "r")
for start, stop in zip(multi_unit.starts, multi_unit.stops):
    this_swr_lfp = lfp.time_slice(start, stop)
    plt.plot(this_swr_lfp.time, this_swr_lfp.data, "y")
for start, stop in zip(these_swrs.starts, these_swrs.stops):
    this_swr_lfp = lfp.time_slice(start, stop)
    plt.plot(this_swr_lfp.time, this_swr_lfp.data, "c")
plt.text(0.01, 0.01, "n_swrs: " + str(swrs.n_epochs), transform=ax.transAxes)
# plt.xlim(prerecord_start, prerecord_stop)
plt.show()
# plt.savefig(os.path.join(output_filepath, info.session_id+"_check-swr-prerecord_zthresh"+str(z_thresh)+".png"))
# plt.close()
