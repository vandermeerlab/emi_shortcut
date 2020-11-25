import numpy as np

import meta
import meta_session
from tasks import task
from utils import latex_float, mannwhitneyu


def group_all(all_props, phases):
    return {
        condition: {
            phase: [prop[condition][phase] for prop in all_props] for phase in phases
        }
        for condition in all_props[0]
    }


@task(groups=meta_session.groups, cache_saves="replay_prop_byphase")
def cache_combined_replay_prop_byphase(
    infos, group_name, *, all_replay_proportions_byphase
):
    return group_all(all_replay_proportions_byphase, meta.task_times)


@task(groups=meta_session.groups, cache_saves="replay_prop_normalized_byphase")
def cache_replay_prop_normalized_byphase(infos, group_name, *, replay_prop_byphase):
    normalized = {}
    for trajectory in replay_prop_byphase:
        if trajectory in ["difference", "contrast", "difference_ph2", "contrast_ph2"]:
            continue
        prop = np.array(list(replay_prop_byphase[trajectory].values()))
        prop /= np.mean(prop)
        normalized[trajectory] = {
            phase: prop[i] for i, phase in enumerate(replay_prop_byphase[trajectory])
        }
    return normalized


@task(groups=meta_session.groups, cache_saves="replay_prop_byexperience_bytrial")
def cache_combined_replay_prop_byexperience_bytrial(
    infos, group_name, *, all_replay_proportions_byexperience_bytrial
):
    return group_all(all_replay_proportions_byexperience_bytrial, meta.experiences)


@task(
    groups=meta_session.groups,
    cache_saves="replay_prop_byexperience_nofeeder_bytrial",
)
def cache_combined_replay_prop_byexperience_nofeeder_bytrial(
    infos, group_name, *, all_replay_proportions_byexperience_nofeeder_bytrial
):
    return group_all(
        all_replay_proportions_byexperience_nofeeder_bytrial, meta.experiences
    )


@task(
    groups=meta_session.groups,
    cache_saves="replay_prop_byexperience_feederonly",
)
def cache_combined_replay_prop_byexperience_feederonly(
    infos, group_name, *, all_replay_proportions_byexperience_feederonly
):
    return group_all(all_replay_proportions_byexperience_feederonly, meta.on_task)


@task(
    groups=meta_session.analysis_grouped,
    savepath=("replays-session", "replay_prop_normalized_byphase_pval.tex"),
)
def save_replay_prop_normalized_byphase_pval(
    infos,
    group_name,
    *,
    replay_prop_normalized_byphase,
    savepath,
):
    with open(savepath, "w") as fp:
        print("% replay prop normalized byphase pval", file=fp)
        pval = mannwhitneyu(
            replay_prop_normalized_byphase["only_u"]["pauseA"],
            replay_prop_normalized_byphase["only_u"]["pauseB"],
        )
        pval = latex_float(pval)
        print(
            fr"\def \replaynormalizeduabpval/{{{pval}}}",
            file=fp,
        )

        pval = mannwhitneyu(
            replay_prop_normalized_byphase["only_full_shortcut"]["phase2"],
            replay_prop_normalized_byphase["only_full_shortcut"]["phase3"],
        )
        pval = latex_float(pval)
        print(
            fr"\def \replaynormalizedfullshortcuttwothreepval/{{{pval}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(
    groups=meta_session.analysis_grouped,
    savepath=("replays", "replay_prop_byphase_pval.tex"),
)
def save_replay_prop_byphase_pval(infos, group_name, *, replay_prop_byphase, savepath):
    phase = "phase3"
    with open(savepath, "w") as fp:
        print("% replay proportions byphase pval", file=fp)
        pval = mannwhitneyu(
            replay_prop_byphase["only_u"][phase],
            replay_prop_byphase["only_full_shortcut"][phase],
        )
        phase = "phasethree" if phase == "phase3" else phase
        print(
            fr"\def \replayprop{phase}pval/{{{latex_float(pval)}}}",
            file=fp,
        )
        print("% ---------", file=fp)


@task(infos=meta_session.analysis_infos, cache_saves="replay_participation")
def cache_replay_participation(info, *, replays_byphase, spikes):
    participation = []

    for replay in replays_byphase["full_shortcut"]["phase3"]:
        assert replay.n_epochs == 1
        replay_spikes = [
            spiketrain.time_slice(replay.start, replay.stop) for spiketrain in spikes
        ]
        participation.append(
            [
                spiketrain.n_spikes >= meta.replay_participation_min_spikes
                for spiketrain in replay_spikes
            ]
        )

    return np.vstack(participation)


@task(infos=meta_session.analysis_infos, cache_saves="full_replay_participation_rate")
def cache_full_replay_participation_rate(info, *, replay_participation):
    return np.mean(replay_participation, axis=0)


@task(infos=meta_session.analysis_infos, cache_saves="replay_participation_rate")
def cache_replay_participation_rate(
    info, *, full_replay_participation_rate, tc_order, tc_order_unique_ph3
):
    return {
        "unique": full_replay_participation_rate[tc_order_unique_ph3],
        "nonunique": full_replay_participation_rate[
            [ix for ix in tc_order["full_shortcut"] if ix not in tc_order_unique_ph3]
        ],
        "nofield": full_replay_participation_rate[
            [
                ix
                for ix in range(full_replay_participation_rate.size)
                if ix not in tc_order["full_shortcut"]
            ]
        ],
    }


@task(groups=meta_session.groups, cache_saves="replay_participation_rate")
def cache_combined_replay_participation_rate(
    infos, group_name, *, all_replay_participation_rate
):
    return {
        key: np.hstack([rate[key] for rate in all_replay_participation_rate])
        for key in all_replay_participation_rate[0]
    }


@task(infos=meta_session.analysis_infos, cache_saves="replay_any_unique_participation")
def cache_replay_any_unique_participation(
    info, *, tc_order_unique_ph3, replays_byphase, spikes
):
    participation = []

    for replay in replays_byphase["full_shortcut"]["phase3"]:
        assert replay.n_epochs == 1
        replay_spikes = [
            spiketrain.time_slice(replay.start, replay.stop) for spiketrain in spikes
        ]
        for ix in tc_order_unique_ph3:
            if replay_spikes[ix].n_spikes >= meta.replay_participation_min_spikes:
                participation.append(True)
                break
        else:
            participation.append(False)

    assert len(participation) == replays_byphase["full_shortcut"]["phase3"].n_epochs
    return np.array(participation)


@task(
    infos=meta_session.analysis_infos,
    cache_saves="replay_any_unique_participation_rate",
)
def cache_replay_any_unique_participation_rate(info, *, replay_unique_participation):
    return np.mean(replay_unique_participation)


@task(groups=meta_session.groups, cache_saves="replay_any_unique_participation_rate")
def cache_combined_any_replay_unique_participation_rate(
    infos, group_name, *, all_replay_unique_participation_rate
):
    return np.hstack([rate for rate in all_replay_unique_participation_rate])
