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
