import matplotlib.pyplot as plt
import numpy as np
import scipy
import pandas as pd
import seaborn as sns
import pickle
import os
import nept

from loading_data import get_data
from analyze_tuning_curves import get_only_tuning_curves
from utils_maze import get_trials

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, "plots", "decode-video")
if not os.path.exists(pickle_filepath):
    os.makedirs(pickle_filepath)
if not os.path.exists(output_filepath):
    os.makedirs(output_filepath)


def get_decoded(info, position, spikes, xedges, yedges, shuffled_id):

    phase = info.task_times["phase3"]
    trials = get_trials(events, phase)

    error_byactual_position = np.zeros((len(yedges), len(xedges)))
    n_byactual_position = np.ones((len(yedges), len(xedges)))

    session_n_active = []
    session_likelihoods = []
    session_decoded = []
    session_actual = []
    session_errors = []
    session_n_running = 0

    for trial in trials:
        epoch_of_interest = phase.excludes(trial)

        tuning_curves = get_only_tuning_curves(position,
                                               spikes,
                                               xedges,
                                               yedges,
                                               epoch_of_interest)

        if shuffled_id:
            tuning_curves = np.random.permutation(tuning_curves)

        sliced_position = position.time_slice(trial.start, trial.stop)

        sliced_spikes = [spiketrain.time_slice(trial.start,
                                               trial.stop) for spiketrain in spikes]

        # limit position to only times when the subject is moving faster than a certain threshold
        run_epoch = nept.run_threshold(sliced_position, thresh=10., t_smooth=0.8)
        sliced_position = sliced_position[run_epoch]

        session_n_running += sliced_position.n_samples

        sliced_spikes = [spiketrain.time_slice(run_epoch.start,
                                               run_epoch.stop) for spiketrain in sliced_spikes]

        # epochs_interest = nept.Epoch(np.array([sliced_position.time[0], sliced_position.time[-1]]))

        counts = nept.bin_spikes(sliced_spikes, sliced_position.time, dt=0.025, window=0.025,
                                 gaussian_std=0.0075, normalized=False)

        min_neurons = 2
        min_spikes = 2

        tc_shape = tuning_curves.shape
        decoding_tc = tuning_curves.reshape(tc_shape[0], tc_shape[1] * tc_shape[2])

        likelihood = nept.bayesian_prob(counts, decoding_tc, binsize=0.025, min_neurons=min_neurons,
                                        min_spikes=min_spikes)

        # Find decoded location based on max likelihood for each valid timestep
        xcenters = (xedges[1:] + xedges[:-1]) / 2.
        ycenters = (yedges[1:] + yedges[:-1]) / 2.
        xy_centers = nept.cartesian(xcenters, ycenters)
        decoded = nept.decode_location(likelihood, xy_centers, counts.time)

        session_decoded.append(decoded)

        # Remove nans from likelihood and reshape for plotting
        keep_idx = np.sum(np.isnan(likelihood), axis=1) < likelihood.shape[1]
        likelihood = likelihood[keep_idx]
        likelihood = likelihood.reshape(np.shape(likelihood)[0], tc_shape[1], tc_shape[2])

        session_likelihoods.append(likelihood)

        n_active_neurons = np.asarray([n_active if n_active >= min_neurons else 0
                                       for n_active in np.sum(counts.data >= 1, axis=1)])
        n_active_neurons = n_active_neurons[keep_idx]
        session_n_active.append(n_active_neurons)

        f_xy = scipy.interpolate.interp1d(sliced_position.time, sliced_position.data.T, kind="nearest")
        counts_xy = f_xy(decoded.time)
        true_position = nept.Position(np.hstack((counts_xy[0][..., np.newaxis],
                                                 counts_xy[1][..., np.newaxis])),
                                      decoded.time)

        session_actual.append(true_position)

        trial_errors = true_position.distance(decoded)
        session_errors.append(trial_errors)

    return session_decoded, session_actual, session_likelihoods, session_errors, session_n_active, session_n_running


def plot_errors(all_errors, all_errors_id_shuffled, n_sessions, filename=None):

    all_errors = np.concatenate([np.concatenate(errors, axis=0) for errors in all_errors], axis=0)
    all_errors_id_shuffled = np.concatenate([np.concatenate(errors, axis=0) for errors in all_errors_id_shuffled], axis=0)

    fliersize = 1

    decoded_dict = dict(error=all_errors, label='Decoded')
    shuffled_id_dict = dict(error=all_errors_id_shuffled, label='ID shuffled')
    decoded_errors = pd.DataFrame(decoded_dict)
    shuffled_id = pd.DataFrame(shuffled_id_dict)
    data = pd.concat([shuffled_id, decoded_errors])
    colours = ['#ffffff', '#bdbdbd']

    plt.figure(figsize=(6, 4))
    flierprops = dict(marker='o', markersize=fliersize, linestyle='none')
    ax = sns.boxplot(x='label', y='error', data=data, flierprops=flierprops)

    edge_colour = '#252525'
    for i, artist in enumerate(ax.artists):
        artist.set_edgecolor(edge_colour)
        artist.set_facecolor(colours[i])

        for j in range(i*6, i*6+6):
            line = ax.lines[j]
            line.set_color(edge_colour)
            line.set_mfc(edge_colour)
            line.set_mec(edge_colour)

    ax.text(1., 1., "N sessions: %d \nmean-error: %.1f cm \nmedian-error: %.1f cm" % (n_sessions,
                                                                                      np.mean(all_errors),
                                                                                      np.median(all_errors)),
            horizontalalignment='right',
            verticalalignment='top',
            transform = ax.transAxes,
            fontsize=10)

    ax.set(xlabel=' ', ylabel="Error (cm)")
    plt.xticks(fontsize=14)

    sns.despine()
    plt.tight_layout()

    if filename is not None:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()


def plot_over_space(values, positions, xedges, yedges):
    xcenters = xedges[:-1] + (xedges[1:] - xedges[:-1]) / 2
    ycenters = yedges[:-1] + (yedges[1:] - yedges[:-1]) / 2

    count_position = np.zeros((len(yedges), len(xedges)))
    n_position = np.ones((len(yedges), len(xedges)))

    for trial_values, trial_positions in zip(values, positions):
        for these_values, x, y in zip(trial_values, trial_positions.x, trial_positions.y):
            x_idx = nept.find_nearest_idx(xcenters, x)
            y_idx = nept.find_nearest_idx(ycenters, y)
            if np.isscalar(these_values):
                count_position[y_idx][x_idx] += these_values
            else:
                count_position[y_idx][x_idx] += these_values[y_idx][x_idx]
            n_position[y_idx][x_idx] += 1

    return count_position / n_position


if __name__ == "__main__":
    import info.r063d2 as r063d2
    import info.r063d3 as r063d3
    infos = [r063d2, r063d3]

    from run import spike_sorted_infos
    # infos = spike_sorted_infos

    for info in infos:
        print(info.session_id)
        events, position, spikes, _, _ = get_data(info)

        # for binsize in [6, 20]:
        for binsize in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 50, 100, 150, 200]:
            print("binsize:", binsize)

            xedge, yedge = nept.get_xyedges(position, binsize=binsize)

            decoded_filename = info.session_id + '_decoded_binsize' + str(binsize) + 'cm.pkl'
            pickled_path = os.path.join(pickle_filepath, decoded_filename)
            decoded, actual, likelihoods, errors, n_active, session_n_running = get_decoded(info,
                                                         position,
                                                         spikes,
                                                         xedge,
                                                         yedge,
                                                         shuffled_id=False)
            output = dict()
            output["decoded"] = decoded
            output["actual"] = actual
            output["likelihoods"] = likelihoods
            output["errors"] = errors
            output["n_active"] = n_active
            output["session_n_running"] = session_n_running
            with open(pickled_path, 'wb') as fileobj:
                pickle.dump(output, fileobj)

            shuffled_filename = info.session_id + '_decoded-shuffled_binsize' + str(binsize) + 'cm.pkl'
            pickled_path = os.path.join(pickle_filepath, shuffled_filename)
            decoded, actual, likelihoods, errors, n_active, session_n_running = get_decoded(info,
                                                         position,
                                                         spikes,
                                                         xedge,
                                                         yedge,
                                                         shuffled_id=True)
            output = dict()
            output["decoded"] = decoded
            output["actual"] = actual
            output["likelihoods"] = likelihoods
            output["errors"] = errors
            output["n_active"] = n_active
            output["session_n_running"] = session_n_running
            output["xedges"] = xedge
            output["yedges"] = yedge
            with open(pickled_path, 'wb') as fileobj:
                pickle.dump(output, fileobj)



        # n_sessions = 0
        # session_ids = []
        # xedges = []
        # yedges = []
        #
        # all_decoded = []
        # all_actual = []
        # all_likelihoods = []
        # all_n_active = []
        #
        # all_errors = []
        # all_errors_id_shuffled = []
        # all_errors_random_shuffled = []
        #
        # proportion_decoded = []
        #
        # for info in infos:
        #     print(info.session_id)
        #     session_ids.append(info.session_id)
        #     n_sessions += 1
        #     events, position, spikes, _, _ = get_data(info)
        #
        #     xedge, yedge = nept.get_xyedges(position, binsize=binsize)
        #     xedges.append(xedge)
        #     yedges.append(yedge)
        #
        #     xx, yy = np.meshgrid(xedge, yedge)
        #
        #     decoded, actual, likelihoods, errors, n_active, session_n_running = get_decoded(info,
        #                                              position,
        #                                              spikes,
        #                                              xedge,
        #                                              yedge,
        #                                              shuffled_id=False)
        #
        #     _, _, _, errors_id_shuffled, _, _ = get_decoded(info,
        #                                          position,
        #                                          spikes,
        #                                          xedge,
        #                                          yedge,
        #                                          shuffled_id=True)
        #
        #     likelihood_byactual = plot_over_space(likelihoods, actual, xedge, yedge)
        #     pp = plt.pcolormesh(xx, yy, likelihood_byactual, vmin=0., cmap='bone_r')
        #     plt.colorbar(pp)
        #     title = info.session_id+" posterior"
        #     plt.title(title)
        #     plt.axis('off')
        #     plt.savefig(os.path.join(output_filepath, info.session_id+"_posterior-byactual.png"))
        #     plt.close()
        #
        #     errors_byactual = plot_over_space(errors, actual, xedge, yedge)
        #     pp = plt.pcolormesh(xx, yy, errors_byactual, vmin=0., cmap='bone_r')
        #     plt.colorbar(pp)
        #     title = info.session_id+" decoding error (cm)"
        #     plt.title(title)
        #     plt.axis('off')
        #     plt.savefig(os.path.join(output_filepath, info.session_id+"_errors-byactual.png"))
        #     plt.close()
        #
        #     n_decoded = 0
        #     for trial in decoded:
        #         n_decoded += trial.n_samples
        #     proportion_decoded.append(n_decoded/session_n_running)
        #
        #     all_decoded.append(decoded)
        #     all_actual.append(actual)
        #     all_likelihoods.append(likelihoods)
        #     all_n_active.append(n_active)
        #
        #     all_errors.append(errors)
        #     all_errors_id_shuffled.append(errors_id_shuffled)
        #
        #     filename = os.path.join(output_filepath, info.session_id+"_errors-binsize"+str(binsize)+".png")
        #     plot_errors([errors], [errors_id_shuffled], n_sessions=1, filename=filename)
        #
        # combined_errors = np.concatenate([np.concatenate(errors, axis=0) for errors in all_errors], axis=0)
        #
        # filename = os.path.join(output_filepath, "combined_errors-binsize"+str(binsize)+".png")
        # plot_errors(all_errors, all_errors_id_shuffled, n_sessions, filename)
        #
        # y_pos = np.arange(n_sessions)
        # plt.bar(y_pos, proportion_decoded, align='center', alpha=0.7)
        # plt.xticks(y_pos, session_ids, rotation=90, fontsize=10)
        # plt.ylabel('Proportion')
        # plt.title("Samples decoded with %d cm bins" % binsize)
        # plt.tight_layout()
        # plt.savefig(os.path.join(output_filepath, "proportion-decoded_"+str(binsize)+"cm.png"))
        # plt.close()
