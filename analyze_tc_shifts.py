import matplotlib.pyplot as plt
import numpy as np
import scipy
import itertools
import os
import nept

from loading_data import get_data
from analyze_tuning_curves import get_tuning_curves
from run import info, spike_sorted_infos

infos = [info.r068d7, info.r068d8]
# infos = spike_sorted_infos

thisdir = os.path.dirname(os.path.realpath(__file__))
pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, "plots", "tc_shift")


def get_pearsons_correlation(info, phase1, phase2, xedges, yedges, position, spikes):
    sliced_position1 = position.time_slice(info.task_times[phase1].start, info.task_times[phase1].stop)
    sliced_spikes1 = [spiketrain.time_slice(info.task_times[phase1].start, info.task_times[phase1].stop) for spiketrain in spikes]
    neurons1 = get_tuning_curves(info, sliced_position1, sliced_spikes1, xedges, yedges, speed_limit=0.4,
                                 phase_id=phase1, min_n_spikes=None, trial_times=None, trial_number=None, cache=False)

    sliced_position2 = position.time_slice(info.task_times[phase2].start, info.task_times[phase2].stop)
    sliced_spikes2 = [spiketrain.time_slice(info.task_times[phase2].start, info.task_times[phase2].stop) for spiketrain in spikes]
    neurons2 = get_tuning_curves(info, sliced_position2, sliced_spikes2, xedges, yedges, speed_limit=0.4,
                                 phase_id=phase2, min_n_spikes=None, trial_times=None, trial_number=None, cache=False)

    shape = neurons1.tuning_shape
    n_neurons = neurons1.n_neurons

    correlation = np.zeros(shape)
    for ii in range(shape[0]):
        for jj in range(shape[1]):
            neurons1_pixel = []
            neurons2_pixel = []
            for neuron in range(n_neurons):
                neurons1_pixel.append(neurons1.tuning_curves[neuron][ii][jj])
                neurons2_pixel.append(neurons2.tuning_curves[neuron][ii][jj])

                correlation[ii][jj] = np.corrcoef(neurons1_pixel, neurons2_pixel)[1, 0]

    return correlation


def find_intersection(info, path_id, xedges, yedges):
    path, _, _ = np.histogram2d([info.path_pts[path_id][0]], [info.path_pts[path_id][1]], bins=[xedges, yedges])
    path_x = np.where(path > 0)[0]
    path_y = np.where(path > 0)[1]

    return path_x, path_y


def find_neighbours(shape, points, neighbour_size):
    grid = np.array(list(itertools.product(np.arange(shape[0]), np.arange(shape[1]))))
    tree = scipy.spatial.KDTree(grid)

    indices = []
    for point in points:
        indices.extend(tree.query_ball_point([point[0][0], point[1][0]], r=neighbour_size))

    return grid[indices]


def compare_correlations(correlations, stable_neighbours, novel_neighbours):
    stable_corr = [correlations[pt[1]][pt[0]] for pt in stable_neighbours]
    novel_corr = [correlations[pt[1]][pt[0]] for pt in novel_neighbours]

    stable = np.nansum(stable_corr) / np.count_nonzero(~np.isnan(stable_corr))
    novel = np.nansum(novel_corr) / np.count_nonzero(~np.isnan(novel_corr))

    return stable, novel


def plot_tc_corr(corr, stable_points, novel_points, filename=None):
    plt.imshow(corr, vmin=0.0, vmax=1.0, cmap="pink_r")
    for point in stable_points:
        plt.plot(point[0], point[1], 'r.', ms=15)
    for point in novel_points:
        plt.plot(point[0], point[1], 'b.', ms=15)
    plt.colorbar()
    plt.axis('off')
    if filename is not None:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    corr_stable12 = []
    corr_stable13 = []
    corr_stable23 = []

    corr_novel12 = []
    corr_novel13 = []
    corr_novel23 = []

    for info in infos:
        events, position, spikes, lfp, lfp_theta = get_data(info)
        xedges, yedges = nept.get_xyedges(position)

        tc_shape = (len(yedges) - 1, len(xedges) - 1)

        shortcut1 = find_intersection(info, "shortcut1", xedges, yedges)
        shortcut2 = find_intersection(info, "shortcut2", xedges, yedges)
        novel1 = find_intersection(info, "novel1", xedges, yedges)
        # novel2 = find_intersection(info, "novel2", xedges, yedges)
        stable1 = find_intersection(info, "stable1", xedges, yedges)

        novel_points = [shortcut1, shortcut2, novel1]
        stable_points = [stable1]
        novel_neighbours = find_neighbours(tc_shape, novel_points, neighbour_size=2)
        stable_neighbours = find_neighbours(tc_shape, stable_points, neighbour_size=2)

        corr12 = get_pearsons_correlation(info, "phase1", "phase2", xedges, yedges, position, spikes)
        corr13 = get_pearsons_correlation(info, "phase1", "phase3", xedges, yedges, position, spikes)
        corr23 = get_pearsons_correlation(info, "phase2", "phase3", xedges, yedges, position, spikes)
        corr33 = get_pearsons_correlation(info, "phase3", "phase3", xedges, yedges, position, spikes)

        stable12, novel12 = compare_correlations(corr12, stable_neighbours, novel_neighbours)
        stable13, novel13 = compare_correlations(corr13, stable_neighbours, novel_neighbours)
        stable23, novel23 = compare_correlations(corr23, stable_neighbours, novel_neighbours)

        if not np.isnan(stable12):
            corr_stable12.append(stable12)
        if not np.isnan(novel12):
            corr_novel12.append(novel12)
        if not np.isnan(stable13):
            corr_stable13.append(stable13)
        if not np.isnan(novel13):
            corr_novel13.append(novel13)
        if not np.isnan(stable23):
            corr_stable23.append(stable23)
        if not np.isnan(novel23):
            corr_novel23.append(novel23)

        print("phases 1 and 2. Average correlation for stable:", stable12, "compared to novel:", novel12, "segments")
        print("phases 1 and 3. Average correlation for stable:", stable13, "compared to novel:", novel13, "segments")
        print("phases 2 and 3. Average correlation for stable:", stable23, "compared to novel:", novel23, "segments")

        filepath = os.path.join(output_filepath, info.session_id + "_phase-shift12.png")
        plot_tc_corr(corr12, stable_neighbours, novel_neighbours, filepath)

        filepath = os.path.join(output_filepath, info.session_id + "_phase-shift13.png")
        plot_tc_corr(corr13, stable_neighbours, novel_neighbours, filepath)

        filepath = os.path.join(output_filepath, info.session_id + "_phase-shift23.png")
        plot_tc_corr(corr23, stable_neighbours, novel_neighbours, filepath)

        filepath = os.path.join(output_filepath, info.session_id + "_phase-shift33.png")
        plot_tc_corr(corr33, stable_neighbours, novel_neighbours, filepath)

    print([corr_stable12, corr_novel12, corr_stable13, corr_novel13, corr_stable23, corr_novel23])

    #Boxplot summary
    fig = plt.figure()
    ax = fig.add_subplot(111)

    boxplot = ax.boxplot([corr_stable12, corr_novel12, corr_stable13, corr_novel13, corr_stable23, corr_novel23],
                         positions=[1, 2, 4, 5, 7, 8], widths=0.75, patch_artist=True)

    colours = ['#bf812d', '#35978f', '#bf812d', '#35978f', '#bf812d', '#35978f']
    for patch, colour in zip(boxplot['boxes'], colours):
        patch.set_facecolor(colour)

    plt.setp(boxplot['medians'], color='k')

    # plt.ylim(0.1, 1.)
    labels = ["Phases 1-2", "Phases 1-3", "Phases 2-3"]
    plt.xticks([1.5, 4.5, 7.5], labels)
    plt.ylabel("Mean correlation")

    hB, = plt.plot([1, 1], '-', color='#bf812d')
    hR, = plt.plot([1, 1], '-', color='#35978f')
    legend = ax.legend((hB, hR), ('Stable segments', 'Novel segments'), bbox_to_anchor=(1., 1.))
    hB.set_visible(False)
    hR.set_visible(False)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.tight_layout()

    filepath = os.path.join(output_filepath, "tuning-curve_shift_summary.png")
    fig.savefig(filepath, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()
    # plt.show()
