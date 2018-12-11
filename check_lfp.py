import matplotlib.pyplot as plt
import os
import numpy as np
import nept

import info.r068d8 as info

thisdir = os.path.dirname(os.path.realpath(__file__))
dataloc = os.path.abspath(os.path.join(thisdir, 'cache', 'data'))
print(dataloc)
lfp = nept.load_lfp(os.path.join(dataloc, info.lfp_swr_filename))

sliced_lfp = lfp.time_slice(4877, 4880)
print(sliced_lfp.data)
plt.plot(sliced_lfp.time, sliced_lfp.data, ".")
plt.show()
