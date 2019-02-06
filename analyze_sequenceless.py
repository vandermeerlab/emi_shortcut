import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import numpy as np
import warnings
import random
import scipy
import pickle
import os
import nept
import scalebar

from loading_data import get_data
from analyze_tuning_curves import get_only_tuning_curves
from utils_maze import get_zones
from utils_maze import get_bin_centers

thisdir = os.getcwd()
pickle_filepath = os.path.join(thisdir, "cache", "pickled")
output_filepath = os.path.join(thisdir, "plots", "trials", "decoding", "classy")
if not os.path.exists(output_filepath):
    os.makedirs(output_filepath)

# Set random seeds
random.seed(0)
np.random.seed(0)


class Session:
    """A collection of LikelihoodsAtTaskTime for each session

        Parameters
        ----------
        task_times : dict of TaskTime

    """

    def __init__(self, position, task_labels, zones):
        self.position = position
        self.task_labels = task_labels
        for task_label in task_labels:
            setattr(self, task_label, TaskTime([], [], [], zones))

    def pickle(self, save_path):
        with open(save_path, 'wb') as fileobj:
            print("Saving " + save_path)
            pickle.dump(self, fileobj)

    def n_tasktimes(self):
        return len(self.task_labels)


class TaskTime:
    """A set of decoded likelihoods for a given task time

        Parameters
        ----------
        likelihoods : np.array
            With shape (ntimebins, nxbins, nybins)
        zones : dict of Zones

        Attributes
        ----------
        likelihoods : np.array
            With shape (ntimebins, nxbins, nybins)

    """

    def __init__(self, tuning_curves, swrs, likelihoods, zones):
        self.tuning_curves = tuning_curves
        self.swrs = swrs
        self.likelihoods = likelihoods
        self.zones = zones

    def sums(self, zone_label):
        return np.nansum(self.likelihoods[:, :, self.zones[zone_label]], axis=2)

    def means(self, zone_label):
        return np.nanmean(self.likelihoods[:, :, self.zones[zone_label]], axis=2)

    def maxes(self, zone_label):
        return np.nanmax(self.likelihoods[:, :, self.zones[zone_label]], axis=2)


def get_likelihoods(info, swr_params, task_labels, zone_labels, n_shuffles=0, save_path=None):
    _, position, spikes, lfp, _ = get_data(info)

    zones = dict()
    zones["u"], zones["shortcut"], zones["novel"] = get_zones(info, position, subset=True)
    combined_zones = zones["u"] + zones["shortcut"] + zones["novel"]
    zones["other"] = ~combined_zones

    if n_shuffles > 0:
        n_passes = n_shuffles
    else:
        n_passes = 1

    session = Session(position, task_labels, zones)

    tuning_curves_fromdata = get_only_tuning_curves(info, position, spikes, info.task_times["phase3"])

    tc_shape = tuning_curves_fromdata.shape

    phase_for_zthresh = "pauseB"

    swrs = nept.detect_swr_hilbert(lfp,
                                   fs=info.fs,
                                   thresh=swr_params["swr_thresh"],
                                   z_thresh=info.lfp_z_thresh,
                                   merge_thresh=swr_params["merge_thresh"],
                                   min_length=swr_params["min_length"],
                                   times_for_z=nept.Epoch(info.task_times[phase_for_zthresh].start,
                                                          info.task_times[phase_for_zthresh].stop))

    swrs = nept.find_multi_in_epochs(spikes, swrs, min_involved=swr_params["min_involved"])

    rest_epochs = nept.rest_threshold(position, thresh=12., t_smooth=0.8)

    for task_label in task_labels:
        epochs_of_interest = info.task_times[task_label].intersect(rest_epochs)

        phase_swrs = epochs_of_interest.overlaps(swrs)
        phase_swrs = phase_swrs[phase_swrs.durations >= 0.05]

        phase_likelihoods = np.zeros((n_passes, phase_swrs.n_epochs, tc_shape[1], tc_shape[2]))
        phase_tuningcurves = np.zeros((n_passes, tc_shape[0], tc_shape[1], tc_shape[2]))
        for n_pass in range(n_passes):

            if n_shuffles > 0:
                tuning_curves = np.random.permutation(tuning_curves_fromdata)
            else:
                tuning_curves = tuning_curves_fromdata

            phase_tuningcurves[n_pass, ] = tuning_curves
            tuning_curves = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

            if phase_swrs.n_epochs == 0:
                phase_likelihoods = np.ones((n_passes, 1, tc_shape[1], tc_shape[2])) * np.nan
            else:
                counts_data = []
                counts_time = []
                t_windows = []

                for n_timebin, (start, stop) in enumerate(zip(phase_swrs.starts,
                                                              phase_swrs.stops)):
                    t_window = stop - start  # 0.1 for running, 0.025 for swr

                    sliced_spikes = [spiketrain.time_slice(start, stop) for spiketrain in spikes]

                    these_counts = nept.bin_spikes(sliced_spikes,
                                                   start,
                                                   stop,
                                                   dt=t_window,
                                                   gaussian_std=0.0075,
                                                   normalized=False)

                    counts_data.append(these_counts.data)
                    counts_time.append(these_counts.time)
                    t_windows.append(t_window)

                counts = nept.AnalogSignal(np.vstack(counts_data), np.hstack(counts_time))
                likelihood = nept.bayesian_prob(counts,
                                                tuning_curves,
                                                binsize=t_windows,
                                                min_neurons=3,
                                                min_spikes=1)

                phase_likelihoods[n_pass] = likelihood.reshape(phase_swrs.n_epochs, tc_shape[1], tc_shape[2])

        tasktime = getattr(session, task_label)
        tasktime.likelihoods = phase_likelihoods
        tasktime.tuning_curves = phase_tuningcurves
        tasktime.swrs = phase_swrs

    if save_path is not None:
        session.pickle(save_path)

    return session


import info.r063d2 as info

# swr params
swr_params = dict()
swr_params["merge_thresh"] = 0.02
swr_params["min_length"] = 0.05
swr_params["swr_thresh"] = (140.0, 250.0)
swr_params["min_involved"] = 4

task_labels = ["prerecord", "pauseA", "pauseB", "postrecord"]
zone_labels = ["u", "shortcut", "novel", "other"]

session = get_likelihoods(info, swr_params, task_labels, zone_labels, n_shuffles=0, save_path=None)
print(session.pauseA.swrs.n_epochs)
