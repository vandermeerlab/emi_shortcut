import os
import numpy as np
import matplotlib.pyplot as plt
import pickle

from load_data import get_pos

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'tuning')


infos = spike_sorted_infos
num = 10

outputs = []
for info in infos:
    for i in list(range(num)):
        outputs.append(os.path.join(output_filepath, info.session_id + '_tuning-curves' + str(i) + '.png'))

def analyze(info, tuning_curve, num=10):
    print('plotting tuning curve:', info.session_id)

    position = get_pos(info.pos_mat, info.pxl_to_cm)

    binsize = 3
    xedges = np.arange(position.x.min(), position.x.max() + binsize, binsize)
    yedges = np.arange(position.y.min(), position.y.max() + binsize, binsize)
    xx, yy = np.meshgrid(xedges, yedges)

    for i, neuron in enumerate(tuning_curve[0:num]):
        pp = plt.pcolormesh(xx, yy, neuron, cmap='YlGn')
        plt.colorbar(pp)
        plt.axis('off')
        savepath = os.path.join(output_filepath, info.session_id + '_tuning-curves_' + str(i) + '.png')
        plt.savefig(savepath)

if __name__ == "__main__":
    from run import spike_sorted_infos
    for info in spike_sorted_infos:
        tuning_curve_filename = info.session_id + '_tuning_curve.pkl'
        pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)

        with open(pickled_tuning_curve, 'rb') as fileobj:
            tuning_curve = pickle.load(fileobj)
        analyze(info, tuning_curve)
