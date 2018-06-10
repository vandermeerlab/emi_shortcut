import matplotlib.pyplot as plt
import numpy as np
import os
import nept

from loading_data import get_data
from analyze_tuning_curves import get_tuning_curves
from analyze_decode import get_decoded, get_decoded_zones

from run import info, spike_sorted_infos

# infos = [info.r066d4, info.r067d4]
infos = spike_sorted_infos

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, "plots", "decode_wout_trial")
# output_filepath = os.path.join(thisdir, "plots", "test")


def decode_trial(info, neurons, trial_times, trial_number, shuffled, random_shuffle=False):
    args = dict(info=info,
                dt=0.025,
                gaussian_std=0.0075,
                min_neurons=2,
                min_spikes=1,
                min_swr=3,
                neurons=neurons,
                normalized=False,
                run_time=True,
                speed_limit=0.4,
                shuffle_id=shuffled,
                window=0.025,
                decoding_times=trial_times,
                min_proportion_decoded=0.1,
                decode_sequences=False,
                random_shuffle=random_shuffle,
                )

    print('decoding: trial %s; shuffled: %s' % (trial_number, shuffled))

    decode = dict()
    decode['decoded'], decode['decoded_epochs'], decode['errors'], decode['position'], decode['likelihood'] = get_decoded(**args)

    return decode


if __name__ == "__main__":
    for random_shuffle in [False, True]:
        shuffled = False
        all_trajectory_errors = dict(u=[], shortcut=[], novel=[])

        for info in infos:
            print(info.session_id)
            events, position, spikes, lfp, lfp_theta = get_data(info)

            position = position.time_slice(info.task_times['phase3'].start, info.task_times['phase3'].stop)
            spikes = [spiketrain.time_slice(info.task_times['phase3'].start, info.task_times['phase3'].stop) for spiketrain in spikes]

            xedges, yedges = nept.get_xyedges(position)

            trial_epochs = get_trials(events, info.task_times['phase3'])

            error_byactual_position = np.zeros((len(yedges), len(xedges)))
            n_byactual_position = np.ones((len(yedges), len(xedges)))

            trajectory_errors = dict(u=[], shortcut=[], novel=[])

            # for trial_idx in range(trial_epochs.n_epochs):
            for trial_idx in range(2):
                trial_start = trial_epochs.starts[trial_idx]
                trial_stop = trial_epochs.stops[trial_idx]

                trial_times = nept.Epoch([trial_start, trial_stop])
                neurons = get_tuning_curves(info, position, spikes, xedges, yedges, speed_limit=0.4,
                                            phase_id="phase3", trial_times=trial_times, trial_number=trial_idx,
                                            cache=False)

                decode = decode_trial(info, neurons, trial_times, trial_idx, shuffled, random_shuffle=True)

                if decode['position'].n_samples > 0:
                    for error, x, y in zip(decode['errors'], decode['position'].x, decode['position'].y):
                        x_idx = nept.find_nearest_idx(xedges, x)
                        y_idx = nept.find_nearest_idx(yedges, y)
                        error_byactual_position[y_idx][x_idx] += error
                        n_byactual_position[y_idx][x_idx] += 1

                    decoded_zones, zone_errors, actual_position = get_decoded_zones(info,
                                                                                    decode["decoded"],
                                                                                    decode["position"],
                                                                                    "phase3")
                    trajectory_errors["u"].extend(zone_errors["u"])
                    trajectory_errors["shortcut"].extend(zone_errors["shortcut"])
                    trajectory_errors["novel"].extend(zone_errors["novel"])

                    all_trajectory_errors["u"].extend(trajectory_errors["u"])
                    all_trajectory_errors["shortcut"].extend(trajectory_errors["shortcut"])
                    all_trajectory_errors["novel"].extend(trajectory_errors["novel"])

            error_byactual = error_byactual_position / n_byactual_position

            xx, yy = np.meshgrid(xedges, yedges)

            print("error")
            pp = plt.pcolormesh(xx, yy, error_byactual, vmin=0., cmap='bone_r')
            plt.colorbar(pp)
            plt.axis('off')
            if random_shuffle:
                filename = "decoding_wout_current_trial-" + info.session_id + "-error-random_shuffled.png"
            elif shuffled:
                filename = "decoding_wout_current_trial-" + info.session_id + "-error-shuffled.png"
            else:
                filename = "decoding_wout_current_trial-" + info.session_id + "-error.png"
            plt.savefig(os.path.join(output_filepath, filename))
            plt.close()

            print("position occupancy")
            pp = plt.pcolormesh(xx, yy, n_byactual_position, vmin=0., vmax=500., cmap="pink_r")
            plt.colorbar(pp)
            plt.axis('off')
            if random_shuffle:
                filename = "decoding_wout_current_trial-" + info.session_id + "-occupancy-random_shuffled.png"
            elif shuffled:
                filename = "decoding_wout_current_trial-" + info.session_id + "-occupancy-shuffled.png"
            else:
                filename = "decoding_wout_current_trial-" + info.session_id + "-occupancy.png"
            plt.savefig(os.path.join(output_filepath, filename))
            plt.close()

            fig, ax = plt.subplots()
            ind = np.arange(3)
            width = 0.9
            means = [np.mean(trajectory_errors['u']),
                     np.mean(trajectory_errors['shortcut']),
                     np.mean(trajectory_errors['novel'])]
            yerr = [np.std(trajectory_errors['u']),
                    np.std(trajectory_errors['shortcut']),
                    np.std(trajectory_errors['novel'])]
            plt.bar(ind, means, width=width, color=["#0072b2ff", "#009e73ff", "#d55e00ff"], yerr=yerr)
            ax.set_xticks(ind + width / 100)
            ax.set_xticklabels(('u', 'shortcut', 'dead-end'))
            ax.set_ylabel('Average error (cm)')
            if random_shuffle:
                filename = "decoding_wout_current_trial-" + info.session_id + "-trajectory_error-random_shuffled.png"
            elif shuffled:
                filename = "decoding_wout_current_trial-" + info.session_id + "-trajectory_error-shuffled.png"
            else:
                filename = "decoding_wout_current_trial-" + info.session_id + "-trajectory_error.png"
            plt.savefig(os.path.join(output_filepath, filename))
            plt.close()

        fig, ax = plt.subplots()
        ind = np.arange(3)
        width = 0.9
        means = [np.mean(all_trajectory_errors['u']),
                 np.mean(all_trajectory_errors['shortcut']),
                 np.mean(all_trajectory_errors['novel'])]
        yerr = [np.std(all_trajectory_errors['u']),
                np.std(all_trajectory_errors['shortcut']),
                np.std(all_trajectory_errors['novel'])]
        print("means:", means, "std:", yerr)
        plt.bar(ind, means, width=width, color=["#0072b2ff", "#009e73ff", "#d55e00ff"], yerr=yerr)
        ax.set_xticks(ind + width / 100)
        ax.set_xticklabels(('u', 'shortcut', 'dead-end'))
        ax.set_ylabel('Average error (cm)')
        if random_shuffle:
            filename = "decoding_wout_current_trial-all-trajectory_error-random_shuffled.png"
        elif shuffled:
            filename = "decoding_wout_current_trial-all-trajectory_error-shuffled.png"
        else:
            filename = "decoding_wout_current_trial-all_trajectory_error.png"
        plt.savefig(os.path.join(output_filepath, filename))
        plt.close()
