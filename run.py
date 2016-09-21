import os
import sys
import pickle

import plot_behavior
import analyze_tuning_curves
import plot_tuning_curves
import plot_decode

import info

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')

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
    if "all" in sys.argv:
        infos = all_infos
    elif "spike_sorted" in sys.argv:
        infos = spike_sorted_infos
    elif "r063" in sys.argv:
        infos = r063_infos
    elif "r066" in sys.argv:
        infos = r066_infos
    elif "r067" in sys.argv:
        infos = r067_infos
    elif "r068" in sys.argv:
        infos = r068_infos
    else:
        print("None of specified infos passed "
              "('all', 'spike_sorted', 'r063', 'r066', 'r067', r068'), "
              "so using all infos.")
        infos = all_infos

    # --- Analyses

    if any(s in sys.argv for s in ["tuning_curves", "plot_tuning_curves", "plot_decode_errors",
                                   "plot_decode_pauses", "plot_decode_phases", "plot_decode_normalized"]):
        outputs = analyze_tuning_curves.get_outputs(infos)
        tuning_curves = []
        if needs_to_run(outputs):
            for info in infos:
                tuning_curves.append(analyze_tuning_curves.analyze(info))
        else:
            for info in infos:
                tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
                pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
                with open(pickled_tuning_curve, 'rb') as fileobj:
                    tuning_curves.append(pickle.load(fileobj))

    if "plot_tuning_curves" in sys.argv:
        outputs = analyze_tuning_curves.get_outputs(infos)
        if needs_to_run(outputs):
            for tuning_curve, info in zip(infos, tuning_curves):
                plot_tuning_curves.plot(info, tuning_curve)

    if "plot_decode_errors" in sys.argv:
        if needs_to_run(plot_decode.outputs_errors):
            plot_decode.plot_errors(infos, tuning_curves)

    if "plot_decode_pauses" in sys.argv:
        if needs_to_run(plot_decode.outputs_pauses):
            plot_decode.plot_pauses(infos, tuning_curves)

    if "plot_decode_phases" in sys.argv:
        if needs_to_run(plot_decode.outputs_phases):
            plot_decode.plot_phases(infos, tuning_curves)

    if "plot_decode_normalized" in sys.argv:
        if needs_to_run(plot_decode.outputs_normalized):
            plot_decode.plot_normalized(infos, tuning_curves)

    if "behavior" in sys.argv:
        if needs_to_run(plot_behavior.outputs):
            plot_behavior.analyze(infos)

