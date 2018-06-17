import matplotlib.pyplot as plt
import numpy as np
import os
import nept
import scipy

from loading_data import extract_xy

thisdir = os.getcwd()
dataloc = os.path.join(thisdir, 'cache', 'data')
pickle_filepath = os.path.join(thisdir, "cache", "pickled")
output_filepath = os.path.join(thisdir, "plots", "correcting_position")

import info.r063d2 as r063d2
info = r063d2

events = nept.load_events(os.path.join(dataloc, info.event_filename), info.event_labels)

# Load raw position from file
filename = os.path.join(dataloc, info.position_filename)
nvt_data = nept.load_nvt(filename)
targets = nvt_data['targets']
times = nvt_data['time']

# Initialize x, y arrays
x = np.zeros(targets.shape)
y = np.zeros(targets.shape)

# X and Y are stored in a custom bitfield. See Neuralynx data file format documentation for details.
# Briefly, each record contains up to 50 targets, each stored in 32bit field.
# X field at [20:31] and Y at [4:15].
# TODO: make into a separate function in nept
for target in range(targets.shape[1]):
    this_sample = targets[:, target]
    for sample in range(targets.shape[0]):
        # When the bitfield is equal to zero there is no valid data for that field
        # and remains zero for the rest of the bitfields in the record.
        if this_sample[target] == 0:
            break
        x[sample, target], y[sample, target] = extract_xy(int(this_sample[sample]))

# Replacing targets with no samples with nan instead of 0
x[x == 0] = np.nan
y[y == 0] = np.nan

# # Scale the positions
scale_targets = 1.9
x /= scale_targets
y /= scale_targets

print("Feeder1")
xmode, xcount = scipy.stats.mode(x, axis=None, nan_policy='omit')
ymode, ycount = scipy.stats.mode(y, axis=None, nan_policy='omit')
print("xy:", xmode, ymode)

print("Feeder2")
xxmode, xxcount = scipy.stats.mode(x[x != xmode], axis=None, nan_policy='omit')
yymode, yycount = scipy.stats.mode(y[y != ymode], axis=None, nan_policy='omit')
print("xy:", xxmode, yymode)

plt.plot(x, y, "y.", ms=3)
cornerx = 42
cornery = 13
plt.plot(cornerx, cornery, "k.")
plt.plot(cornerx, cornery+30*3, "k.")
plt.plot(cornerx+30*4, cornery, "k.")

for pt in info.path_pts.keys():
    plt.plot(info.path_pts[pt][0], info.path_pts[pt][1], "r.", ms=10)
plt.show()
