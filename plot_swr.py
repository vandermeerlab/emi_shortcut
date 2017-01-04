import os
import vdmlab as vdm

from loading_data import get_data
from utils_plotting import plot_swrs

from run import spike_sorted_infos
infos = spike_sorted_infos


thisdir = os.path.dirname(os.path.realpath(__file__))
output_filepath = os.path.join(thisdir, 'plots', 'swr')


for info in infos:
    print('SWR:', info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)

    thresh = (140.0, 250.0)
    swrs = vdm.detect_swr_hilbert(lfp, fs=info.fs, thresh=thresh)

    filename = info.session_id + '-swr_'
    saveloc = os.path.join(output_filepath, filename)
    plot_swrs(lfp, swrs, saveloc)
