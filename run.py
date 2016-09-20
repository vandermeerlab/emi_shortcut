import os
import sys

import shortcut_behavior

import info

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'behavior')

all_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6, info.r063d7, info.r063d8,
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6, info.r066d7, info.r066d8,
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5, info.r067d6, info.r067d7, info.r067d8,
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6, info.r068d7, info.r068d8]

spike_sorted_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6,
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6,
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5,
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6]

r063_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6, info.r063d7, info.r063d8]

r066_infos = [
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6, info.r066d7, info.r066d8]

r067_infos = [
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5, info.r067d6, info.r067d7, info.r067d8]

r068_infos = [
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6, info.r068d7, info.r068d8]


def needs_to_run(paths):
    if "clear" in sys.argv:
        for path in paths:
            os.remove(path)
        return True

    for path in paths:
        if not os.path.exists(path):
            return True
    return False

if __name__ == "__main__":
    # The block below lets you tell run.py which info files you want to deal with.
    # They are defined with names above (eg. all_infos, spike_sorted_infos).

    if "all" in sys.argv:
        infos = all_infos
    elif "spike_sorted" in sys.argv:
        infos = spike_sorted_infos
    else:
        print("Neither 'all' nor 'spike_sorted' passed, so using all infos.")
        infos = all_infos

    # --- Analyses

    if "behavior" in sys.argv:
        if needs_to_run(shortcut_behavior.outputs):
            shortcut_behavior.analyze(infos)

    # If you do run `analyze` multiple times for different parameters sets,
    # then you should also be able to get the output files for those parameter
    # sets (e.g., using an `outputs` function that takes in the parameter
    # values and returns the list of paths). That way you can use needs_to_run
    # and pass in a list of files for that specific parameter set.
