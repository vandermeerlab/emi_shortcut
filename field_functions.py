def unique_fields(fields, fields_compare1, fields_compare2):
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
