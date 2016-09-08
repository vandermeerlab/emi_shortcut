import numpy as np
from shapely.geometry import Point
import vdmlab as vdm


def get_edges(position, binsize, lastbin=False):
    """Finds edges based on linear time

    Parameters
    ----------
    position : vdmlab.Position
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
    edges = np.arange(position.time[0], position.time[-1], binsize)

    if lastbin:
        if edges[-1] != position.time[-1]:
            edges = np.hstack((edges, position.time[-1]))

    return edges


def point_in_zones(position, zones):
    """Assigns points if contained in shortcut zones

    Parameters
    ----------
    position : vdmlab.Position
    zones : dict
        With u, ushort, unovel, shortcut, shortped, novel, novelped, pedestal as keys

    Returns
    -------
    sorted_zones : dict
        With u, shortcut, novel, other as keys, each a vdmlab.Position object

    """
    u_data = []
    u_times = []
    shortcut_data = []
    shortcut_times = []
    novel_data = []
    novel_times = []
    other_data = []
    other_times = []

    for x, y, time in zip(position.x, position.y, position.time):
        point = Point([x, y])
        if zones['u'].contains(point) or zones['ushort'].contains(point) or zones['unovel'].contains(point):
            u_data.append([x, y])
            u_times.append(time)
            continue
        elif zones['shortcut'].contains(point) or zones['shortped'].contains(point):
            shortcut_data.append([x, y])
            shortcut_times.append(time)
            continue
        elif zones['novel'].contains(point) or zones['novelped'].contains(point):
            novel_data.append([x, y])
            novel_times.append(time)
            continue
        else:
            other_data.append([x, y])
            other_times.append(time)

    sorted_zones = dict()
    sorted_zones['u'] = vdm.Position(u_data, u_times)
    sorted_zones['shortcut'] = vdm.Position(shortcut_data, shortcut_times)
    sorted_zones['novel'] = vdm.Position(novel_data, novel_times)
    sorted_zones['other'] = vdm.Position(other_data, other_times)

    return sorted_zones


def compare_rates(zones, jump=0.1):
    """Compare position normalized by time spent in zone.

    Parameters
    ----------
    zones: dict
        With u, shortcut, novel, other as keys.
    jump: float
        Any duration above this amount will not be included.

    Returns
    -------
    normalized : dict
        With u, shortcut, novel, other as keys.

    """
    u_linger = np.diff(zones['u'].time)
    shortcut_linger = np.diff(zones['shortcut'].time)
    novel_linger = np.diff(zones['novel'].time)
    other_linger = np.diff(zones['other'].time)

    u_linger = np.sum(u_linger[u_linger < jump])
    shortcut_linger = np.sum(shortcut_linger[shortcut_linger < jump])
    novel_linger = np.sum(novel_linger[novel_linger < jump])
    other_linger = np.sum(other_linger[other_linger < jump])

    normalized = dict()
    normalized['u'] = len(zones['u'].time) / u_linger
    normalized['shortcut'] = len(zones['shortcut'].time) / shortcut_linger
    normalized['novel'] = len(zones['novel'].time) / novel_linger
    if len(zones['other'].time) > 20:
        normalized['other'] = len(zones['other'].time) / other_linger
    else:
        normalized['other'] = np.nan

    return normalized
