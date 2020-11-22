import csv

import nept
import numpy as np
import pandas as pd
import scipy.stats
import statsmodels.api as sm

import meta
import meta_session
from tasks import task
from utils import latex_float, ranksum_test, save_ttest_results


@task(infos=meta_session.all_infos, cache_saves="raw_trials")
def cache_raw_trials(info, *, events, task_times):
    stops = []
    for phase in meta.run_times:
        stops.extend(
            events["feederoff"][
                (task_times[phase].stop > events["feederoff"])
                & (events["feederoff"] > task_times[phase].start)
            ]
        )
    stops = stops[1:]  # First stop is from an incomplete trial
    starts = [
        min(
            events["pb1id"][events["pb1id"] < stop][-1],
            events["pb2id"][events["pb2id"] < stop][-1],
        )
        for stop in stops
    ]

    # Remove trials in which the rat passed the photobeam before the recording
    # started at the start of a new phase
    to_remove = []
    phase = 1
    for i, (start, stop) in enumerate(zip(starts, stops)):
        times = task_times[f"phase{phase}"]
        if not times.contains(stop):
            phase += 1
            times = task_times[f"phase{phase}"]
        assert times.contains(stop)
        if not times.contains(start):
            to_remove.append(i)
    for i in reversed(to_remove):
        del starts[i]
        del stops[i]

    return nept.Epoch(starts, stops)


@task(
    infos=meta_session.all_infos,
    cache_saves="trials",
    savepath=("ind-trials", "report.txt"),
)
def cache_trials(info, *, raw_trials, raw_position_byzone, zones, savepath):
    fp = open(savepath, "w")

    dt = np.median(np.diff(raw_position_byzone["u"].time))
    median_trial_duration = np.median(raw_trials.durations)
    print(f"{info.session_id}\n", file=fp)
    print(f"median_trial_duration: {median_trial_duration}", file=fp)
    u_area = zones["u"].area
    u_shortcut_overlap = zones["u"].intersection(zones["full_shortcut"]).area / u_area
    print(f"u_shortcut_overlap: {u_shortcut_overlap}", file=fp)
    u_novel_overlap = zones["u"].intersection(zones["novel"]).area / u_area
    print(f"u_novel_overlap: {u_novel_overlap}\n", file=fp)

    trials = {trial_type: nept.Epoch([], []) for trial_type in meta.trial_types}
    for i, raw_trial in enumerate(raw_trials):
        manual = False
        for trial_type in meta.trial_types:
            if i in info.trials.manual[trial_type]:
                print(
                    f"Raw trial {i}, {trial_type} trial {trials[trial_type].n_epochs} "
                    "(manual)\n",
                    file=fp,
                )
                trials[trial_type] = trials[trial_type].join(raw_trial)
                manual = True
                break
        if manual:
            continue

        assert len(raw_trial.durations) == 1
        exploratory_duration = raw_trial.durations[0] - median_trial_duration
        trial_pos = {
            trajectory: raw_position_byzone[trajectory][raw_trial]
            for trajectory in meta.behavioral_trajectories
        }
        n_samples = sum(pos.n_samples for pos in trial_pos.values())
        if n_samples == 0:
            print(
                f"Raw trial {i} ignored, has no position data for any zone\n", file=fp
            )
            continue
        prop_u = trial_pos["u"].n_samples / n_samples
        prop_full_shortcut = trial_pos["full_shortcut"].n_samples / n_samples

        def classify(trial_type):
            print(f"{trial_type} trial {trials[trial_type].n_epochs}", file=fp)
            trials[trial_type] = trials[trial_type].join(raw_trial)

        print(f"Raw trial {i}", file=fp)
        if trial_pos["novel"].n_samples * dt >= meta.novel_min_duration:
            classify("novel")
        elif exploratory_duration >= meta.exploratory_max_duration:
            classify("exploratory")
        elif prop_full_shortcut >= meta.trial_min_prop:
            classify("full_shortcut")
        elif prop_u + u_shortcut_overlap + u_novel_overlap >= meta.trial_min_prop:
            classify("u")
        else:
            classify("exploratory")

        print(
            f"  novel_duration={trial_pos['novel'].n_samples * dt}\n"
            f"  exploratory_duration={exploratory_duration}\n"
            f"  prop_u={prop_u + u_shortcut_overlap + u_novel_overlap}\n"
            f"  prop_full_shortcut={prop_full_shortcut}\n",
            file=fp,
        )

    fp.close()
    return trials


@task(infos=meta_session.all_infos, cache_saves="matched_trials")
def cache_matched_trials(info, *, trials):
    n_u_trials = trials["u"].n_epochs
    n_shortcut_trials = trials["full_shortcut"].n_epochs

    if n_u_trials > n_shortcut_trials:
        trials["u"] = trials["u"][-n_shortcut_trials:]
        trials["shortcut"] = trials["full_shortcut"]
    elif n_shortcut_trials > n_u_trials:
        trials["full_shortcut"] = trials["full_shortcut"][:n_u_trials]
        trials["shortcut"] = trials["full_shortcut"]

    assert trials["u"].n_epochs == trials["shortcut"].n_epochs
    return trials


@task(infos=meta_session.all_infos, cache_saves="n_trials_ph3")
def cache_n_trials_ph3(info, *, task_times, trials):
    ph3 = task_times["phase3"]
    return {
        trajectory: trials[trajectory].time_slice(ph3.start, ph3.stop).n_epochs
        for trajectory in meta.trial_types
    }


@task(infos=meta_session.all_infos, cache_saves="trial_proportions")
def cache_trial_proportions(info, *, n_trials_ph3):
    n_trials_total = sum(n_trials_ph3[trajectory] for trajectory in meta.trial_types)
    assert n_trials_total > 0
    return {
        trajectory: n_trials_ph3[trajectory] / n_trials_total
        for trajectory in meta.trial_types
    }


@task(groups=meta_session.all_grouped, cache_saves="trial_proportions_df")
def cache_trial_proportions_df(infos, group_name, *, all_trial_proportions):
    trial_proportions_df = []
    for info, trial_proportion in zip(infos, all_trial_proportions):
        trial_proportions_df.extend(
            {
                "proportions": trial_proportion[trajectory],
                "trajectory": trajectory,
                "rat_id": info.session_id[:4],
                "session": info.session_id[-1],
            }
            for trajectory in meta.trial_types
        )
    return pd.DataFrame.from_dict(trial_proportions_df)


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "stats_trial_proportions.tex"),
)
def save_trial_proportion_stats(infos, group_name, *, trial_proportions_df, savepath):
    save_ttest_results(trial_proportions_df, "proportions", savepath)


@task(groups=meta_session.groups, cache_saves="n_trials_ph3")
def cache_combined_n_trials_ph3(infos, group_name, *, all_n_trials_ph3):
    return {
        trajectory: sum(n_trials_ph3[trajectory] for n_trials_ph3 in all_n_trials_ph3)
        for trajectory in meta.trial_types
    }


@task(groups=meta_session.groups, cache_saves="trial_proportions")
def cache_combined_trial_proportions(infos, group_name, *, all_trial_proportions):
    return {
        trajectory: [
            trial_proportions[trajectory] for trial_proportions in all_trial_proportions
        ]
        for trajectory in meta.trial_types
    }


@task(infos=meta_session.all_infos, cache_saves="trial_durations")
def cache_trial_durations(info, *, task_times, trials):
    durations = {}
    for phase in meta.run_times:
        ep = task_times[phase]
        durations[phase] = {
            trajectory: trials[trajectory]
            .time_slice(ep.start, ep.stop)
            .durations.tolist()
            for trajectory in meta.trial_types
        }
    return durations


@task(groups=meta_session.all_grouped, cache_saves="trial_durations_df")
def cache_trial_durations_df(infos, group_name, *, all_trial_durations):
    trial_durations_df = []
    for info, trial_durations in zip(infos, all_trial_durations):
        for phase in meta.run_times:
            for trajectory in meta.trial_types:
                trial_durations_df.extend(
                    {
                        "durations": trial,
                        "phase": phase,
                        "trajectory": trajectory,
                        "rat_id": info.session_id[:4],
                        "session": info.session_id[-1],
                    }
                    for trial in trial_durations[phase][trajectory]
                )
    return pd.DataFrame.from_dict(trial_durations_df)


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "stats_trial_durations.tex"),
)
def save_trial_durations_stats(infos, group_name, *, trial_durations_df, savepath):
    save_ttest_results(trial_durations_df, "durations", savepath)


@task(groups=meta_session.groups, cache_saves="trial_durations")
def cache_combined_trial_durations(infos, group_name, *, all_trial_durations):
    combined = {}
    for phase in meta.run_times:
        combined[phase] = {trajectory: [] for trajectory in meta.trial_types}
        for trajectory in meta.trial_types:
            for trial_durations in all_trial_durations:
                combined[phase][trajectory].extend(trial_durations[phase][trajectory])
        combined[phase] = {
            trajectory: np.array(combined[phase][trajectory])
            for trajectory in meta.trial_types
        }

    return combined


@task(infos=meta_session.all_infos, cache_saves="trial_proportions_bytrial")
def cache_trial_proportions_bytrial(info, *, task_times, trials):
    ph3 = task_times["phase3"]
    trial_type = [
        (t_start, trajectory)
        for trajectory in meta.trial_types
        for t_start in trials[trajectory].time_slice(ph3.start, ph3.stop).starts
    ]
    trial_type.sort()
    trial_type = np.array([trajectory for _, trajectory in trial_type])

    return {
        trajectory: np.array(trial_type == trajectory, dtype=float)
        for trajectory in meta.trial_types
    }


@task(groups=meta_session.groups, cache_saves="trial_proportions_bytrial")
def cache_combined_trial_proportions_bytrial(
    infos, group_name, *, all_trial_proportions_bytrial
):
    return {
        trajectory: [
            [
                trial_type[trajectory][i]
                for trial_type in all_trial_proportions_bytrial
                if trial_type[trajectory].size > i
            ]
            for i in range(
                max(
                    trial_type[trajectory].size
                    for trial_type in all_trial_proportions_bytrial
                )
            )
        ]
        for trajectory in meta.trial_types
    }


@task(infos=meta_session.all_infos, cache_saves="trial_durations_bytrial")
def cache_trial_durations_bytrial(info, *, task_times, trials):
    ph3 = task_times["phase3"]

    durations = {}
    for trajectory in meta.trial_types:
        traj_trials = trials[trajectory].time_slice(ph3.start, ph3.stop)
        durations[trajectory] = traj_trials.durations
    return durations


@task(groups=meta_session.groups, cache_saves="trial_durations_bytrial")
def cache_combined_trial_durations_bytrial(
    infos, group_name, *, all_trial_durations_bytrial
):
    all_durations = {}
    for trajectory in meta.trial_types:
        max_trials = max(
            len(durations[trajectory]) for durations in all_trial_durations_bytrial
        )
        all_durations[trajectory] = []
        for i in range(max_trials):
            all_durations[trajectory].append(
                [
                    durations[trajectory][i]
                    for durations in all_trial_durations_bytrial
                    if len(durations[trajectory]) > i
                ]
            )
    return all_durations


def get_directional_trials(info, position, trials, task_times):
    directional_trials = {
        trajectory: {"feeder1": nept.Epoch([], []), "feeder2": nept.Epoch([], [])}
        for trajectory in meta.behavioral_trajectories
    }

    for trajectory in meta.behavioral_trajectories:
        for trial in trials[trajectory]:
            trial_position = position[trial]
            dist = {}
            for feeder in ["feeder1", "feeder2"]:
                dist[feeder] = np.sqrt(
                    (info.path_pts[feeder][0] - trial_position.data[0][0]) ** 2
                    + (info.path_pts[feeder][1] - trial_position.data[0][1]) ** 2
                )
            start_location = next(
                key
                for key in dist
                if dist[key] == min([dist["feeder1"], dist["feeder2"]])
            )
            directional_trials[trajectory][start_location] = directional_trials[
                trajectory
            ][start_location].join(trial)
    directional_trials["u_phase3"] = {
        "feeder1": nept.Epoch([], []),
        "feeder2": nept.Epoch([], []),
    }
    ph3 = task_times["phase3"]
    for feeder in ["feeder1", "feeder2"]:
        directional_trials["u_phase3"][feeder] = directional_trials["u"][
            feeder
        ].time_slice(ph3.start, ph3.stop)
    return directional_trials


@task(infos=meta_session.all_infos, cache_saves="directional_trials")
def cache_directional_trials(info, *, position, trials, task_times):
    return get_directional_trials(info, position, trials, task_times)


@task(groups=meta_session.all_grouped, savepath=("behavior", "n_trials.table"))
def save_n_trials(infos, group_name, *, all_directional_trials, savepath):
    with open(savepath, "w") as fp:
        print(
            r"""
            \begin{tabular}{c | r r c}
 \toprule
 \textbf{Rat~ID} & \textbf{Familiar} & \textbf{Shortcut} & \textbf{Dead-end} \\ [0.5ex]
 \midrule
 """.strip(),
            file=fp,
        )
        for info, directional_trials in zip(infos, all_directional_trials):
            dir_u1 = directional_trials["u"]["feeder1"].n_epochs
            dir_u2 = directional_trials["u"]["feeder2"].n_epochs
            dir_shortcut1 = directional_trials["full_shortcut"]["feeder1"].n_epochs
            dir_shortcut2 = directional_trials["full_shortcut"]["feeder2"].n_epochs
            dir_novel1 = directional_trials["novel"]["feeder1"].n_epochs
            dir_novel2 = directional_trials["novel"]["feeder2"].n_epochs
            print(
                rf"\textbf{{{info.session_id}}} & {dir_u1 + dir_u2} ({dir_u1} $\mid$ {dir_u2}) & "
                rf"{dir_shortcut1 + dir_shortcut2} ({dir_shortcut1} $\mid$ {dir_shortcut2}) "
                rf"& {dir_novel1 + dir_novel2} \\",
                file=fp,
            )
            if info.session_id in ["R063d8", "R066d8", "R067d8"]:
                print(r"\midrule", file=fp)

        print(r"\bottomrule", file=fp)
        print(r"\end{tabular}", file=fp)


@task(groups=meta_session.all_grouped, savepath=("behavior", "n_trials_phase3.table"))
def save_n_trials_phase3(infos, group_name, *, all_directional_trials, savepath):
    with open(savepath, "w") as fp:
        print(
            r"""
            \begin{tabular}{c | r r c}
 \toprule
 \textbf{Rat~ID} & \textbf{Familiar} & \textbf{Shortcut} & \textbf{Dead-end} \\ [0.5ex]
 \midrule
 """.strip(),
            file=fp,
        )
        for info, directional_trials in zip(infos, all_directional_trials):
            dir_u1 = directional_trials["u_phase3"]["feeder1"].n_epochs
            dir_u2 = directional_trials["u_phase3"]["feeder2"].n_epochs
            dir_shortcut1 = directional_trials["full_shortcut"]["feeder1"].n_epochs
            dir_shortcut2 = directional_trials["full_shortcut"]["feeder2"].n_epochs
            dir_novel1 = directional_trials["novel"]["feeder1"].n_epochs
            dir_novel2 = directional_trials["novel"]["feeder2"].n_epochs
            print(
                rf"\textbf{{{info.session_id}}} & {dir_u1 + dir_u2} ({dir_u1} $\mid$ {dir_u2}) & "
                rf"{dir_shortcut1 + dir_shortcut2} ({dir_shortcut1} $\mid$ {dir_shortcut2}) "
                rf"& {dir_novel1 + dir_novel2} \\",
                file=fp,
            )
            if info.session_id in ["R063d8", "R066d8", "R067d8"]:
                print(r"\midrule", file=fp)

        print(r"\bottomrule", file=fp)
        print(r"\end{tabular}", file=fp)


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "percent_trials_phase3.tex"),
)
def save_percent_trials_phase3(
    infos,
    group_name,
    *,
    all_task_times,
    all_trials,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% Number of trials in Phase3", file=fp)
        n_trials = {trajectory: 0 for trajectory in meta.trial_types}
        for task_times, trials in zip(all_task_times, all_trials):
            ph3 = task_times["phase3"]
            for trajectory in meta.trial_types:
                n_trials[trajectory] += (
                    trials[trajectory].time_slice(ph3.start, ph3.stop).n_epochs
                )
        n_total = sum(n_trials.values())

        for trajectory in meta.trial_types:
            traj = trajectory.replace("_", "")
            print(
                fr"\def \percent{traj}trialsphasethree/{{{n_trials[trajectory] / n_total * 100:.1f}}}",
                file=fp,
            )
        print("% ---------", file=fp)


@task(groups=meta_session.all_grouped, savepath=("behavior", "behavior_choice.tex"))
def save_trial_proportions(
    infos,
    group_name,
    *,
    all_trial_proportions,
    trial_proportions,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% Trial choices", file=fp)
        for info, this_trial_proportions in zip(infos, all_trial_proportions):
            print(f"% {info.session_id}", file=fp)
            for trajectory in meta.trial_types:
                proportion = this_trial_proportions[trajectory] * 100
                print(
                    f"% {trajectory}: {proportion:.1f}",
                    file=fp,
                )
            print("% ---------", file=fp)
        print("% Combined (mean)", file=fp)
        for trajectory in meta.trial_types:
            traj = trajectory.replace("_", "")

            proportion = np.mean(trial_proportions[trajectory]) * 100
            print(
                fr"\def \n{traj}trials/{{{proportion:.1f}}}",
                file=fp,
            )
        print("% ---------", file=fp)


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "behavior_choice_firsttrial.tex"),
)
def save_firsttrial_proportions(
    infos,
    group_name,
    *,
    trial_proportions_bytrial,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% First trial choices", file=fp)
        for trajectory in meta.trial_types:
            traj = trajectory.replace("_", "")
            props = trial_proportions_bytrial[trajectory][0]
            print(
                fr"\def \percent{traj}firsttrials/{{{np.mean(props) * 100:.1f}}}",
                file=fp,
            )
        print("% ---------", file=fp)


@task(groups=meta_session.all_grouped, savepath=("behavior", "trial_durations.tex"))
def save_behavior_durations(infos, group_name, *, all_trial_durations, savepath):
    with open(savepath, "w") as fp:
        print("% Trial durations", file=fp)
        all_firsttrial = []
        firsttrial = {trajectory: [] for trajectory in meta.trial_types}
        alltrials = {trajectory: [] for trajectory in meta.trial_types}
        for info, trial_durations in zip(infos, all_trial_durations):
            print(f"% {info.session_id}", file=fp)
            for trajectory in meta.trial_types:
                traj = trajectory.replace("_", "")
                print(f"% {trajectory}", file=fp)
                durations = trial_durations["phase3"][trajectory]
                if len(durations) > 0:
                    firsttrial[trajectory].append(durations[0])
                    all_firsttrial.append(durations[0])
                    alltrials[trajectory].extend(durations)
                    print(f"% first trial duration: {durations[0]:.1f}", file=fp)
                    print(f"% mean duration: {np.mean(durations):.1f}", file=fp)
                    print(f"% shortest duration: {np.min(durations):.1f}", file=fp)
                    print(f"% longest duration: {np.max(durations):.1f}", file=fp)
                else:
                    print("% no trials", file=fp)
                print("% ---------", file=fp)
            print("", file=fp)
        print("% Combined", file=fp)
        for trajectory in meta.trial_types:
            traj = trajectory.replace("_", "")
            print(f"% {trajectory}", file=fp)
            print(
                fr"\def \mean{traj}firsttrialduration/{{{np.mean(firsttrial[trajectory]):.1f}}}",
                file=fp,
            )
            print(
                fr"\def \mean{traj}duration/{{{np.mean(alltrials[trajectory]):.1f}}}",
                file=fp,
            )
            print(
                fr"\def \shortest{traj}trial/{{{np.min(alltrials[trajectory]):.1f}}}",
                file=fp,
            )
            print(
                fr"\def \longest{traj}trial/{{{np.max(alltrials[trajectory]):.1f}}}",
                file=fp,
            )
            print("% ---------", file=fp)
        print(
            fr"\def \meanallfirsttrialduration/{{{np.mean(all_firsttrial):.1f}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(infos=meta_session.all_infos, cache_saves="mostly_shortcut_idx")
def cache_mostly_shortcut_idx(info, *, trial_proportions_bytrial):
    above_thresh = np.asarray(
        np.array(
            [np.mean(trial) for trial in trial_proportions_bytrial["full_shortcut"]]
        )
        >= meta.mostly_thresh,
        dtype=int,
    )
    for ix, val in enumerate(above_thresh):
        if val == 1 and ix > 0 and above_thresh[ix - 1] > 0:
            above_thresh[ix] += above_thresh[ix - 1]

    long_enough = np.where(above_thresh > meta.mostly_n_trials)[0]
    if long_enough.size > 0:
        return long_enough[0] - meta.mostly_n_trials
    return np.nan


@task(groups=meta_session.groups, cache_saves="mostly_shortcut_idx")
def cache_combined_mostly_shortcut_idx(infos, group_name, *, trial_proportions_bytrial):
    above_thresh = np.asarray(
        np.array(
            [np.mean(trial) for trial in trial_proportions_bytrial["full_shortcut"]]
        )
        >= meta.mostly_thresh,
        dtype=int,
    )
    for ix, val in enumerate(above_thresh):
        if val == 1 and ix > 0 and above_thresh[ix - 1] > 0:
            above_thresh[ix] += above_thresh[ix - 1]

    long_enough = np.where(above_thresh > meta.mostly_n_trials)[0]
    if long_enough.size > 0:
        return long_enough[0] - meta.mostly_n_trials
    return np.nan


@task(
    groups=meta_session.groups,
    savepath=("behavior", f"mostly_shortcut_idx.tex"),
)
def save_mostly_shortcut_idx(infos, group_name, *, mostly_shortcut_idx, savepath):
    with open(savepath, "w") as fp:
        if np.isnan(mostly_shortcut_idx):
            print("% Last trial is below threshold", file=fp)
        else:
            tex_id = meta.tex_ids[group_name]

            print(
                fr"\def \mostlyshortcutpercent{tex_id}/{{{meta.mostly_thresh * 100:.0f}}}",
                file=fp,
            )
            print(
                fr"\def \mostlyshortcuttrial{tex_id}/{{{mostly_shortcut_idx + 1}}}",
                file=fp,
            )
            print(
                f"% More than {meta.mostly_thresh * 100:.0f}% shortcut trials at trial "
                f"% {mostly_shortcut_idx + 1}",
                file=fp,
            )


@task(
    groups=meta_session.all_grouped, savepath=("behavior", "behavior_duration_pval.tex")
)
def save_behavior_duration_pval(
    infos,
    group_name,
    *,
    trial_durations,
    savepath,
):
    t, pval, df = sm.stats.ttest_ind(
        trial_durations["phase3"]["u"], trial_durations["phase3"]["full_shortcut"]
    )
    with open(savepath, "w") as fp:
        print("% Behavior Duration pval", file=fp)
        for trajectory in meta.trial_types:
            traj = trajectory.replace("_", "")
            totalmeandurations = np.mean(trial_durations["phase3"][trajectory])
            totalsemdurations = scipy.stats.sem(trial_durations["phase3"][trajectory])
            print(
                fr"\def \totalmeandurations{traj}/{{{totalmeandurations:.2f}}}",
                file=fp,
            )
            print(
                fr"\def \totalsemdurations{traj}/{{{totalsemdurations:.2f}}}",
                file=fp,
            )
        print(
            fr"\def \totaldurationststat/{{{t:.2f}}}",
            file=fp,
        )
        pval = latex_float(pval)
        print(
            fr"\def \totaldurationspval/{{{pval}}}",
            file=fp,
        )
        print(
            fr"\def \totaldurationsdf/{{{int(df)}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(
    groups=meta_session.all_grouped, savepath=("behavior", "behavior_choice_pval.tex")
)
def save_behavior_choice_pval(
    infos,
    group_name,
    *,
    trial_proportions,
    n_trials_ph3,
    savepath,
):
    n_trials_total = n_trials_ph3["u"] + n_trials_ph3["full_shortcut"]
    pval = ranksum_test(
        xn=n_trials_ph3["u"],
        xtotal=n_trials_total,
        yn=n_trials_ph3["full_shortcut"],
        ytotal=n_trials_total,
    )
    pval = latex_float(pval)
    with open(savepath, "w") as fp:
        print("% Behavior choice pval", file=fp)
        print(
            fr"\def \behaviorchoicepval/{{{pval}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "behavior_choice_firsttrial_pval.tex"),
)
def save_behavior_choice_firsttrial_pval(
    infos,
    group_name,
    *,
    trial_proportions_bytrial,
    savepath,
):
    firsttrial_proportions = {
        trajectory: trial_proportions_bytrial[trajectory][0]
        for trajectory in meta.trial_types
    }
    pval = ranksum_test(
        xn=int(sum(firsttrial_proportions["u"])),
        xtotal=len(firsttrial_proportions["u"]),
        yn=int(sum(firsttrial_proportions["full_shortcut"])),
        ytotal=len(firsttrial_proportions["full_shortcut"]),
    )
    pval = latex_float(pval)
    with open(savepath, "w") as fp:
        print("% Behavior choice pval", file=fp)
        print(
            fr"\def \behaviorchoicefirsttrialpval/{{{pval}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(
    groups=meta_session.all_grouped,
    savepath=("behavior", "trial_times.csv"),
)
def save_trial_times_csv(
    infos,
    group_name,
    *,
    all_trials,
    savepath,
):
    f = open(savepath, "w")
    f.truncate()
    with open(savepath, "a+", newline="") as write_obj:
        csv_writer = csv.writer(write_obj)
        headings = ["Rat ID", "Session", "Trial type", "Start", "Stop"]
        csv_writer.writerow(headings)
        for info, trials in zip(infos, all_trials):
            for trajectory in meta.trial_types:
                for trial in trials[trajectory]:
                    this_trial = [
                        info.session_id[:4],
                        info.session_id[-1],
                        meta.trial_types_labels[trajectory],
                        trial.start,
                        trial.stop,
                    ]
                    csv_writer.writerow(this_trial)
    f.close()
