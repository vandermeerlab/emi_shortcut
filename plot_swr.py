import os
import vdmlab as vdm

from loading_data import get_data
from analyze_plotting import plot_swrs

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
import info.R063d4_info as r063d4
import info.R063d5_info as r063d5
import info.R063d6_info as r063d6
import info.R066d1_info as r066d1
import info.R066d2_info as r066d2
import info.R066d3_info as r066d3
import info.R066d4_info as r066d4
import info.R067d1_info as r067d1

import info.R068d1_info as r068d1


thisdir = os.path.dirname(os.path.realpath(__file__))

output_filepath = os.path.join(thisdir, 'plots', 'swr')


# infos = [r068d1]
infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4, r067d1]

for info in infos:
    print('Working on ' + info.session_id)

    events, position, spikes, lfp, lfp_theta = get_data(info)

    thresh = (140.0, 250.0)
    swrs = vdm.detect_swr_hilbert(lfp, fs=info.fs, thresh=thresh)

    filename = info.session_id + '-swr_'
    saveloc = os.path.join(output_filepath, filename)
    plot_swrs(lfp, swrs, saveloc)
