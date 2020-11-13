import numpy as np

import meta
import meta_session
from tasks import task


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
        if trajectory in ["difference", "contrast"]:
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
