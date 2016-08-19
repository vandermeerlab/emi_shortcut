import numpy as np

def get_edges(linear, binsize, lastbin=False):
    """Finds edges based on linear time

    Parameters
    ----------
    linear : vdmlab.Position
        Must be a linear (1D) position
    binsize : float
        This is the desired size of bin.
        Typically set around 0.020 to 0.040 seconds.
    lastbin : boolean
        Determines whether to include the last bin. This last bin may
        not have the same binsize as the other bins.

    Returns
    -------
    edges : np.array

    """
    edges = np.arange(linear.time[0], linear.time[-1], binsize)

    if lastbin:
        if edges[-1] != linear.time[-1]:
            edges = np.hstack((edges, linear.time[-1]))

    return edges
