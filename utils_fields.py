import numpy as np
from shapely.geometry import Point
from scipy import ndimage
import nept

from utils_maze import get_bin_centers


def get_unique_fields(fields, fields_compare1, fields_compare2):
    """ Finds neurons with and indices of unique fields.

    Parameters
    ----------
    fields : dict
        Where the key is the neuron number (int), value is a list of arrays (int).
        Each inner array contains the indices for a given place field.
    fields_compare1 : dict
        Where the key is the neuron number (int), value is a list of arrays (int).
        Each inner array contains the indices for a given place field.\
        May be generated with more restrictive parameters (Eg. hz_thresh=3,
        max_length=tc.shape[0])
    fields_compare2 : dict
        Where the key is the neuron number (int), value is a list of arrays (int).
        Each inner array contains the indices for a given place field.
        May be generated with more restrictive parameters (Eg. hz_thresh=3,
        max_length=tc.shape[0])

    Returns
    -------
    fields_unique : dict
        Where the key is the neuron number (int), value is a list of arrays (int).
        Each inner array contains the indices for a given place field.
        Eg. Neurons 7, 3, 11 that have 2, 1, and 3 place fields respectively would be:
        {7: [[field], [field]], 3: [[field]], 11: [[field], [field], [field]]}

    """
    fields_unique = dict()
    for neuron in fields.keys():
        if neuron not in fields_compare1.keys() and neuron not in fields_compare2.keys():
            fields_unique[neuron] = fields[neuron]
    return fields_unique


def get_field_mask(tuning_curves, field_thresh):
    """Finds mask for field detection from 2D tuning curves.

    Parameters
    ----------
    tuning_curves: list of np.arrays
        Where each inner array is the tuning curve for an individual neuron.
    field_thresh: float

    Returns
    -------
    field_mask: list of bool arrays

    """
    field_mask = []

    for tuning_curve in tuning_curves:
        mask = tuning_curve > field_thresh

        # Remove noise
        open_field = ndimage.binary_opening(mask)
        field_mask.append(ndimage.binary_closing(open_field))

    return field_mask


def categorize_fields(tuning_curves, zone, xedges, yedges, field_thresh):
    """Sorts tuning curves into zones based on peak tuning.

    Parameters
    ----------
    tuning_curves: list of np.arrays
        Where each inner array is the tuning curve for an individual neuron.
    zone: dict
        With u, ushort, unovel, shortcut, shortped, novel, novelped, pedestal keys.
        Each contains a shapely.Polygon object as values.
    xedges: np.array
    yedges: np.array
    field_thresh: float

    Returns
    -------
    fields_tc: dict
        With u, shortcut, novel (dict) as keys.
        Each inner dict contains the index for the neuron as a key and
        the tuning curve as the value.
    """

    field_masks = get_field_mask(tuning_curves, field_thresh)

    xcenters, ycenters = get_bin_centers(info)

    xy_centers = nept.cartesian(xcenters, ycenters)

    fields_tc = dict(u=dict(), shortcut=dict(), novel=dict(), pedestal=dict())

    for i, field_mask in enumerate(field_masks):
        field = xy_centers[np.ravel(field_mask)]

        for pt in field:
            point = Point([pt[0], pt[1]])
            if (i not in fields_tc['u']) and (zone['u'].contains(point)):
                fields_tc['u'][i] = tuning_curves[i]

            if (i not in fields_tc['shortcut']) and (zone['shortcut'].contains(point)):
                fields_tc['shortcut'][i] = tuning_curves[i]

            if (i not in fields_tc['novel']) and (zone['novel'].contains(point)):
                    fields_tc['novel'][i] = tuning_curves[i]
    return fields_tc
