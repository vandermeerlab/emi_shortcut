import os
import sys
import pickle

import plot_behavior
import analyze_tuning_curves
import plot_tuning_curves
import plot_decode
import plot_cooccur

import info

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')

spike_sorted_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6, info.r063d7, info.r063d8,
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6, info.r066d7,
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5, info.r067d6, info.r067d7,
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6, info.r068d7, info.r068d8]

error_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6, info.r063d7,
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6, info.r066d7,
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5,
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6, info.r068d7, info.r068d8]

behavior_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6, info.r063d7, info.r063d8,
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6, info.r066d7, info.r066d8,
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5, info.r067d6, info.r067d7, info.r067d8,
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6, info.r068d7,  info.r068d8]

r063_infos = [
    info.r063d2, info.r063d3, info.r063d4, info.r063d5, info.r063d6, info.r063d7, info.r063d8]

r066_infos = [
    info.r066d1, info.r066d2, info.r066d3, info.r066d4, info.r066d5, info.r066d6, info.r066d7, info.r066d8]

r067_infos = [
    info.r067d1, info.r067d2, info.r067d3, info.r067d4, info.r067d5, info.r067d6, info.r067d8, info.r067d8]

r068_infos = [
    info.r068d1, info.r068d2, info.r068d3, info.r068d4, info.r068d5, info.r068d6, info.r068d7, info.r068d8]

day1_infos = [info.r066d1, info.r067d1, info.r068d1]

day2_infos = [info.r063d2, info.r066d2, info.r067d2, info.r068d2]

day3_infos = [info.r063d3, info.r066d3, info.r067d3, info.r068d3]

day4_infos = [info.r063d4, info.r066d4, info.r067d4, info.r068d4]

day5_infos = [info.r063d5, info.r066d5, info.r067d5, info.r068d5]

day6_infos = [info.r063d6, info.r066d6, info.r067d6, info.r068d6]

day7_infos = [info.r063d7, info.r066d7, info.r067d7, info.r068d7]

day8_infos = [info.r063d8, info.r066d8, info.r067d8, info.r068d8]

days1234_infos = [info.r066d1, info.r067d1, info.r068d1,
                 info.r063d2, info.r066d2, info.r067d2, info.r068d2,
                 info.r063d3, info.r066d3, info.r067d3, info.r068d3,
                 info.r063d4, info.r066d4, info.r067d4, info.r068d4]

days5678_infos = [info.r063d5, info.r066d5, info.r067d5, info.r068d5,
                 info.r063d6, info.r066d6, info.r067d6, info.r068d6,
                 info.r063d7, info.r066d7, info.r067d7, info.r068d7,
                 info.r063d8, info.r066d8, info.r067d8, info.r068d8]

days123_infos = [info.r066d1, info.r067d1, info.r068d1,
                 info.r063d2, info.r066d2, info.r067d2, info.r068d2,
                 info.r063d3, info.r066d3, info.r067d3, info.r068d3]

days456_infos = [info.r063d4, info.r066d4, info.r067d4, info.r068d4,
                  info.r063d5, info.r066d5, info.r067d5, info.r068d5,
                  info.r063d6, info.r066d6, info.r067d6, info.r068d6]

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
    if "spike_sorted" in sys.argv:
        infos = spike_sorted_infos
    elif "r063" in sys.argv:
        infos = r063_infos
    elif "r066" in sys.argv:
        infos = r066_infos
    elif "r067" in sys.argv:
        infos = r067_infos
    elif "r068" in sys.argv:
        infos = r068_infos
    elif "all_sessions" in sys.argv:
        infos = behavior_infos
    elif "early_sessions" in sys.argv:
        infos = days1234_infos
    elif "late_sessions" in sys.argv:
        infos = days5678_infos
    else:
        print("Using spike sorted infos.")
        infos = spike_sorted_infos

    # --- Analyses

    if any(s in sys.argv for s in ["tuning_curves", "plot_tuning_curves", "plot_cooccur", "plot_decode_errors",
                                   "plot_decode_pauses", "plot_decode_phases", "plot_decode_normalized"]):
        if "tc_all" in sys.argv:
            outputs = analyze_tuning_curves.get_outputs_all(infos)
        else:
            outputs = analyze_tuning_curves.get_outputs(infos)
        tuning_curves = []
        for info, outfile in zip(infos, outputs):
            if needs_to_run([outfile]):
                if "tc_all" in sys.argv:
                    tuning_curves.append(analyze_tuning_curves.analyze(info, use_all_tracks=True))
                else:
                    tuning_curves.append(analyze_tuning_curves.analyze(info))
            else:
                if "tc_all" in sys.argv:
                    tuning_curve_filename = info.session_id + '_tuning-curve_all-phases.pkl'
                else:
                    tuning_curve_filename = info.session_id + '_tuning-curve.pkl'
                pickled_tuning_curve = os.path.join(pickle_filepath, tuning_curve_filename)
                with open(pickled_tuning_curve, 'rb') as fileobj:
                    tuning_curves.append(pickle.load(fileobj))

    if "behavior" in sys.argv:
        if needs_to_run(plot_behavior.outputs):
            plot_behavior.analyze(infos)

    if "plot_cooccur" in sys.argv:
        outputs = plot_cooccur.get_outputs_combined_weighted(infos)
        if needs_to_run(outputs):
            plot_cooccur.plot(infos)

    if "plot_decode_errors_all_tracks-trajectories" in sys.argv:
        all_tracks_tc = True
        outputs = plot_decode.get_outputs_errors(infos, all_tracks_tc)
        if needs_to_run(outputs):
            plot_decode.plot_errors(infos, tuning_curves, by_trajectory=True)

    if "plot_decode_errors_all_trajectories" in sys.argv:
        all_tracks_tc = False
        outputs = plot_decode.get_outputs_errors(infos, all_tracks_tc)
        if needs_to_run(outputs):
            plot_decode.plot_errors(infos, tuning_curves, by_trajectory=True)

    if "plot_decode_normalized" in sys.argv:
        outputs = plot_decode.get_outputs_normalized(infos)
        if needs_to_run(outputs):
            plot_decode.plot_normalized(infos, tuning_curves)

    if "plot_decode_pauses" in sys.argv:
        outputs = plot_decode.get_outputs_pauses(infos)
        if needs_to_run(outputs):
            plot_decode.plot_pauses(infos, tuning_curves)

    if "plot_decode_phases" in sys.argv:
        outputs = plot_decode.get_outputs_phases(infos)
        if needs_to_run(outputs):
            plot_decode.plot_phases(infos, tuning_curves)

    if "plot_tuning_curves" in sys.argv:
        outputs = analyze_tuning_curves.get_outputs(infos)
        # if needs_to_run(outputs):
        for tuning_curve, info in zip(infos, tuning_curves):
            plot_tuning_curves.plot(info, tuning_curve)
