import os
import os.path
import shutil
import sys

import svgutils.transform as sg

import paths
from tasks import FigureTask, Task, task


class RectElement(sg.FigureElement):
    def __init__(self, x, y):
        s = 18
        rect = sg.etree.Element(
            sg.SVG + "rect",
            {
                "x": str(x),
                "y": str(y - s),
                "width": str(s),
                "height": str(s),
                "style": "fill:white;",
            },
        )
        sg.FigureElement.__init__(self, rect)


def el(char, path, x, y, scale=1, offset=(10, 30)):
    toret = []
    if char is not None:
        toret.append(RectElement(x + offset[0], y + offset[1]))
        toret.append(
            sg.TextElement(
                x + offset[0], y + offset[1], char, size=36, weight="bold", font="Arial"
            )
        )
    if path.endswith(".svg"):
        svg = sg.fromfile(path)
        svg = svg.getroot()
        svg.moveto(str(x), str(y), scale)
        return [svg] + toret


def svgfig(w, h):
    w = str(w)
    h = str(h)
    return sg.SVGFigure(w, h)


def savefig(fig, out):
    fig.save("%s" % out)
    print("Saved %s" % out)


def day_rat_details(panels, savepath):
    padding = 50
    full_width = 2000 + padding
    full_height = 2000 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["day1"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["day2"],
            630 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(None, panels["day3"], 20 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["day4"], 630 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["day5"], 20 + padding, 1000 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(
            None,
            panels["day6"],
            630 + padding,
            1000 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(None, panels["day7"], 20 + padding, 1500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(
            None,
            panels["day8"],
            630 + padding,
            1500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("B", panels["rat1"], 1300 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(
            None,
            panels["rat2"],
            1300 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["rat3"],
            1300 + padding,
            1000 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["rat4"],
            1300 + padding,
            1500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


def day_details(panels, savepath):
    padding = 50
    full_width = 2500 + padding
    full_height = 1000 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            None,
            panels["day1"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["day2"],
            630 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(None, panels["day3"], 1240 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["day4"], 1850 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["day5"], 20 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(
            None,
            panels["day6"],
            630 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["day7"],
            1240 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["day8"],
            1850 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


def rat_details(panels, savepath):
    padding = 50
    full_width = 1200 + padding
    full_height = 900 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            None,
            panels["rat1"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["rat2"],
            600 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(None, panels["rat3"], 20 + padding, 450 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["rat4"], 600 + padding, 450 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-all", "mazes", "std_distortion_u.svg"),
        "B": ("grp-all", "mazes", "std_distortion_full_shortcut.svg"),
    },
    savepath=("figures", "maze.svg"),
    copy_to="maze.pdf",
)
def fig_maze(panels, savepath):
    padding = 50
    full_width = 1200 + padding
    full_height = 450 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("B", panels["B"], 600 + padding, 20 + padding / 2, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-all", "behavior", "behavior_choice.svg"),
        "B": ("grp-all", "behavior", "behavior_duration.svg"),
        "C": ("grp-all", "behavior", "behavior_bytrial_first_n.svg"),
        "D": ("grp-all", "pos", "speed_byphase_full.svg"),
    },
    savepath=("figures", "behavior.svg"),
    copy_to="behavior.pdf",
)
def fig_behavior(panels, savepath):
    padding = 50
    full_width = 1250 + padding
    full_height = 950 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("B", panels["B"], 630 + padding, 20 + padding / 2, offset=(-padding / 3, 0))
    )
    fig.append(
        el("C", panels["C"], 20 + padding / 2, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["D"], 630 + padding / 2, 500 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-all", "behavior", "behavior_barriers.svg"),
        "B": ("grp-day7_beh", "behavior", "behavior_barriers.svg"),
        "C": ("grp-all", "behavior", "behavior_choice_firsttrial.svg"),
        "D": ("grp-all", "behavior", "behavior_firsttrial.svg"),
    },
    savepath=("figures", "behavior_supplemental.svg"),
    copy_to="behavior_supplemental.pdf",
)
def fig_behavior_supplemental(panels, savepath):
    padding = 20
    full_width = 1200 + padding
    full_height = 1000 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el("A", panels["A"], 20 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("B", panels["B"], 630 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("C", panels["C"], 20 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["D"], 630 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "day1": ("grp-day1", "behavior", "behavior_choice.svg"),
        "day2": ("grp-day2", "behavior", "behavior_choice.svg"),
        "day3": ("grp-day3", "behavior", "behavior_choice.svg"),
        "day4": ("grp-day4_beh", "behavior", "behavior_choice.svg"),
        "day5": ("grp-day5_beh", "behavior", "behavior_choice.svg"),
        "day6": ("grp-day6_beh", "behavior", "behavior_choice.svg"),
        "day7": ("grp-day7_beh", "behavior", "behavior_choice.svg"),
        "day8": ("grp-day8", "behavior", "behavior_choice.svg"),
        "rat1": ("grp-r063", "behavior", "behavior_choice.svg"),
        "rat2": ("grp-r066", "behavior", "behavior_choice.svg"),
        "rat3": ("grp-r067beh", "behavior", "behavior_choice.svg"),
        "rat4": ("grp-r068", "behavior", "behavior_choice.svg"),
    },
    savepath=("figures", "behavior_prop_details.svg"),
    copy_to="behavior_prop_details.pdf",
)
def fig_beh_proportions_details(panels, savepath):
    day_rat_details(panels, savepath)


@task(
    panels={
        "day1": ("grp-day1", "behavior", "behavior_choice.svg"),
        "day2": ("grp-day2", "behavior", "behavior_choice.svg"),
        "day3": ("grp-day3", "behavior", "behavior_choice.svg"),
        "day4": ("grp-day4_beh", "behavior", "behavior_choice.svg"),
        "day5": ("grp-day5_beh", "behavior", "behavior_choice.svg"),
        "day6": ("grp-day6_beh", "behavior", "behavior_choice.svg"),
        "day7": ("grp-day7_beh", "behavior", "behavior_choice.svg"),
        "day8": ("grp-day8", "behavior", "behavior_choice.svg"),
    },
    savepath=("figures", "behavior_prop_day_details.svg"),
    copy_to="behavior_prop_day_details.pdf",
)
def fig_beh_proportions_day_details(panels, savepath):
    day_details(panels, savepath)


@task(
    panels={
        "rat1": ("grp-r063", "behavior", "behavior_choice.svg"),
        "rat2": ("grp-r066", "behavior", "behavior_choice.svg"),
        "rat3": ("grp-r067beh", "behavior", "behavior_choice.svg"),
        "rat4": ("grp-r068", "behavior", "behavior_choice.svg"),
    },
    savepath=("figures", "behavior_prop_rat_details.svg"),
    copy_to="behavior_prop_rat_details.pdf",
)
def fig_beh_proportions_rat_details(panels, savepath):
    rat_details(panels, savepath)


@task(
    panels={
        "day1": ("grp-day1", "behavior", "behavior_bytrial_first_n.svg"),
        "day2": ("grp-day2", "behavior", "behavior_bytrial_first_n.svg"),
        "day3": ("grp-day3", "behavior", "behavior_bytrial_first_n.svg"),
        "day4": ("grp-day4_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day5": ("grp-day5_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day6": ("grp-day6_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day7": ("grp-day7_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day8": ("grp-day8", "behavior", "behavior_bytrial_first_n.svg"),
        "rat1": ("grp-r063", "behavior", "behavior_bytrial_first_n.svg"),
        "rat2": ("grp-r066", "behavior", "behavior_bytrial_first_n.svg"),
        "rat3": ("grp-r067beh", "behavior", "behavior_bytrial_first_n.svg"),
        "rat4": ("grp-r068", "behavior", "behavior_bytrial_first_n.svg"),
    },
    savepath=("figures", "behavior_bytrial_details.svg"),
    copy_to="behavior_bytrial_details.pdf",
)
def fig_beh_bytrial_details(panels, savepath):
    day_rat_details(panels, savepath)


@task(
    panels={
        "day1": ("grp-day1", "behavior", "behavior_bytrial_first_n.svg"),
        "day2": ("grp-day2", "behavior", "behavior_bytrial_first_n.svg"),
        "day3": ("grp-day3", "behavior", "behavior_bytrial_first_n.svg"),
        "day4": ("grp-day4_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day5": ("grp-day5_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day6": ("grp-day6_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day7": ("grp-day7_beh", "behavior", "behavior_bytrial_first_n.svg"),
        "day8": ("grp-day8", "behavior", "behavior_bytrial_first_n.svg"),
    },
    savepath=("figures", "behavior_bytrial_day_details.svg"),
    copy_to="behavior_bytrial_day_details.pdf",
)
def fig_beh_bytrial_day_details(panels, savepath):
    day_details(panels, savepath)


@task(
    panels={
        "rat1": ("grp-r063", "behavior", "behavior_bytrial_first_n.svg"),
        "rat2": ("grp-r066", "behavior", "behavior_bytrial_first_n.svg"),
        "rat3": ("grp-r067beh", "behavior", "behavior_bytrial_first_n.svg"),
        "rat4": ("grp-r068", "behavior", "behavior_bytrial_first_n.svg"),
    },
    savepath=("figures", "behavior_bytrial_rat_details.svg"),
    copy_to="behavior_bytrial_rat_details.pdf",
)
def fig_beh_bytrial_rat_details(panels, savepath):
    rat_details(panels, savepath)


@task(
    panels={
        "A": ("ind-R066d5", "ind-tcs", "tc_full_shortcut_18.svg"),
        "B": ("grp-combined", "tcs", "tc_mean_u.svg"),
        "C": ("grp-combined", "tcs", "tc_mean_full_shortcut.svg"),
        "D": ("grp-combined", "tcs", "tc_correlations_within_phase.svg"),
    },
    savepath=("figures", "tuning_curves.svg"),
    copy_to="tuning_curves.pdf",
)
def fig_tuning_curves(panels, savepath):
    padding = 20
    full_width = 1200 + padding
    full_height = 1250 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el("A", panels["A"], 200 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("B", panels["B"], 20 + padding, 350 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("C", panels["C"], 550 + padding, 350 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["D"], 20 + padding, 800 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-combined", "tcs", "tc_correlations_proportion.svg"),
        "B": ("grp-combined", "tcs", "tc_field_remapping.svg"),
        "C": ("grp-combined", "tcs", "tc_appear_maxpeaks_phase2.svg"),
        "D": ("grp-combined", "tcs", "tc_appear_maxpeaks_phase3.svg"),
        "E": ("grp-combined", "tcs", "tc_disappear_maxpeaks_phase1.svg"),
        "F": ("grp-combined", "tcs", "tc_disappear_maxpeaks_phase2.svg"),
    },
    savepath=("figures", "tuning_curves_supplemental.svg"),
    copy_to="tuning_curves_supplemental.pdf",
)
def fig_tuning_curves_supplemental(panels, savepath):
    padding = 20
    full_width = 2050 + padding
    full_height = 1000 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el("A", panels["A"], 20 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("B", panels["B"], 1400 + padding, 30 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("C", panels["C"], 120 + padding, 550 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["D"], 550 + padding, 550 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["E"], 1050 + padding, 550 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(None, panels["F"], 1510 + padding, 550 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-combined", "tcs", "tc_correlations_proportion.svg"),
        "B": ("grp-combined", "tcs", "tc_field_remapping.svg"),
        "C": ("grp-combined", "tcs", "tc_appear_maxpeaks_phase2.svg"),
        "D": ("grp-combined", "tcs", "tc_appear_maxpeaks_phase3.svg"),
        "E": ("grp-combined", "tcs", "tc_disappear_maxpeaks_phase1.svg"),
        "F": ("grp-combined", "tcs", "tc_disappear_maxpeaks_phase2.svg"),
    },
    savepath=("figures", "tuning_curves_supplemental_ppt.svg"),
    copy_to="tuning_curves_supplemental_ppt.pdf",
)
def fig_tuning_curves_supplemental_ppt(panels, savepath):
    padding = 20
    full_width = 1600 + padding
    full_height = 1400 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el("E", panels["A"], 180 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("F", panels["B"], 20 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(
            "G",
            panels["C"],
            630 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(None, panels["D"], 1100 + padding, 500 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el(
            "H",
            panels["E"],
            630 + padding,
            950 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(None, panels["F"], 1100 + padding, 950 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("ind-R066d1", "swrs", "swrs_in_position.svg"),
        "B": ("ind-R068d1", "swrs", "swrs_overtime.svg"),
        "C": ("grp-combined", "swrs", "swr_rate_byphase_rest.svg"),
        "D": ("grp-combined", "pos", "speed_byphase_rest.svg"),
        "E": ("grp-combined", "swrs", "swr_by_std_rate_full.svg"),
        "F": ("grp-combined", "swrs", "swr_durations_histogram.svg"),
    },
    savepath=("figures", "swr.svg"),
    copy_to="swr.pdf",
)
def fig_swr(panels, savepath):
    padding = 50
    full_width = 1400 + padding
    full_height = 1350 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            40 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("B", panels["B"], 400 + padding, 20 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("C", panels["C"], 100 + padding, 380 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["D"], 730 + padding, 380 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("E", panels["E"], 20 + padding, 860 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("F", panels["F"], 900 + padding, 860 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("ind-R068d1", "replays", "replays_overtime-u.svg"),
        "B": ("ind-R068d1", "replays", "replays_overtime-full_shortcut.svg"),
        "C": ("grp-combined", "swrs", "correlation_hist-u.svg"),
        "D": ("grp-combined", "swrs", "correlation_hist-full_shortcut.svg"),
    },
    savepath=("figures", "replay.svg"),
    copy_to="replay.pdf",
)
def fig_replay(panels, savepath):
    padding = 50
    full_width = 1200 + padding
    full_height = 1100 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            180 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["B"],
            180 + padding,
            320 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("B", panels["C"], 20 + padding, 700 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("C", panels["D"], 660 + padding, 700 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-combined", "swrs", "swr_rate_byphase_rest.svg"),
        "B": ("ind-R068d1", "replays", "replays_overtime-u.svg"),
        "C": ("ind-R068d1", "replays", "replays_overtime-full_shortcut.svg"),
        "D": ("grp-combined", "swrs", "correlation_hist-u.svg"),
        "E": ("grp-combined", "swrs", "correlation_hist-full_shortcut.svg"),
    },
    savepath=("figures", "replay_ppt.svg"),
    copy_to="replay_ppt.pdf",
)
def fig_replay_ppt(panels, savepath):
    padding = 50
    full_width = 1500 + padding
    full_height = 1100 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            0 + padding,
            100 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            600 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["C"],
            600 + padding,
            320 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("D", panels["D"], 140 + padding, 650 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("E", panels["E"], 750 + padding, 650 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-combined", "replays", "overlapping_replay_proportions_byphase.svg"),
        "B": ("grp-combined", "replays", "contrast_replay_proportions_byphase.svg"),
        "C": (
            "grp-combined",
            "replays",
            "exclusive_replay_proportions_normalized_byphase_u.svg",
        ),
        "D": (
            "grp-combined",
            "replays",
            "exclusive_replay_proportions_normalized_byphase_full_shortcut.svg",
        ),
        "E": (
            "grp-combined",
            "replays",
            "overlapping_replay_proportions_byexperience.svg",
        ),
        "F": (
            "grp-combined",
            "replays",
            "contrast_replay_proportions_byexperience.svg",
        ),
    },
    savepath=("figures", "replay_summary.svg"),
    copy_to="replay_summary.pdf",
)
def fig_replay_summary(panels, savepath):
    padding = 50
    full_width = 1300 + padding
    full_height = 1400 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            650 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("C", panels["C"], 20 + padding, 480 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["D"], 650 + padding, 480 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("E", panels["E"], 20 + padding, 960 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("F", panels["F"], 650 + padding, 960 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-combined", "replays", "overlapping_replay_proportions_byphase.svg"),
        "B": ("grp-combined", "replays", "contrast_replay_proportions_byphase.svg"),
        "C": (
            "grp-combined",
            "replays",
            "exclusive_replay_proportions_normalized_byphase_u.svg",
        ),
        "D": (
            "grp-combined",
            "replays",
            "exclusive_replay_proportions_normalized_byphase_full_shortcut.svg",
        ),
    },
    savepath=("figures", "replay_summary_byphase.svg"),
    copy_to="replay_summary_byphase.pdf",
)
def fig_replay_summary_byphase(panels, savepath):
    padding = 50
    full_width = 1300 + padding
    full_height = 900 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            650 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el("C", panels["C"], 20 + padding, 480 + padding, offset=(-padding / 3, 0))
    )
    fig.append(
        el("D", panels["D"], 650 + padding, 480 + padding, offset=(-padding / 3, 0))
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": (
            "grp-combined",
            "replays",
            "overlapping_replay_proportions_byexperience.svg",
        ),
        "B": (
            "grp-combined",
            "replays",
            "contrast_replay_proportions_byexperience.svg",
        ),
        "C": (
            "grp-combined",
            "replays",
            "overlapping_replay_proportions_byexperience_feederonly.svg",
        ),
        "D": (
            "grp-combined",
            "replays",
            "contrast_replay_proportions_byexperience_feederonly.svg",
        ),
    },
    savepath=("figures", "replay_summary_byexperience.svg"),
    copy_to="replay_summary_byexperience.pdf",
)
def fig_replay_summary_byexperience(panels, savepath):
    padding = 50
    full_width = 1300 + padding
    full_height = 900 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            650 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "C",
            panels["C"],
            20 + padding,
            450 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "D",
            panels["D"],
            650 + padding,
            450 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "day1": ("grp-day1", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day2": ("grp-day2", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day3": ("grp-day3", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day4": ("grp-day4", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day5": ("grp-day5", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day6": ("grp-day6", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day7": ("grp-day7", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day8": ("grp-day8", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat1": ("grp-r063", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat2": ("grp-r066", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat3": ("grp-r067", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat4": ("grp-r068", "replays", "exclusive_replay_proportions_byphase.svg"),
    },
    savepath=("figures", "replay_details.svg"),
    copy_to="replay_details.pdf",
)
def fig_replay_details(panels, savepath):
    day_rat_details(panels, savepath)


@task(
    panels={
        "day1": ("grp-day1", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day2": ("grp-day2", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day3": ("grp-day3", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day4": ("grp-day4", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day5": ("grp-day5", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day6": ("grp-day6", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day7": ("grp-day7", "replays", "exclusive_replay_proportions_byphase.svg"),
        "day8": ("grp-day8", "replays", "exclusive_replay_proportions_byphase.svg"),
    },
    savepath=("figures", "replay_day_details.svg"),
    copy_to="replay_day_details.pdf",
)
def fig_replay_day_details(panels, savepath):
    day_details(panels, savepath)


@task(
    panels={
        "rat1": ("grp-r063", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat2": ("grp-r066", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat3": ("grp-r067", "replays", "exclusive_replay_proportions_byphase.svg"),
        "rat4": ("grp-r068", "replays", "exclusive_replay_proportions_byphase.svg"),
    },
    savepath=("figures", "replay_rat_details.svg"),
    copy_to="replay_rat_details.pdf",
)
def fig_replay_rat_details(panels, savepath):
    rat_details(panels, savepath)


@task(
    panels={
        "A": ("grp-combined", "decoding", "std_error.svg"),
        "B": ("grp-combined", "decoding", "std_error_bybin.svg"),
        "C": (
            "grp-combined",
            "decoding",
            "replay_likelihood_bybin.svg",
        ),
        "D": (
            "grp-combined",
            "decoding",
            "zscored_logodds_byphase.svg",
        ),
    },
    savepath=("figures", "decoding.svg"),
    copy_to="decoding.pdf",
)
def fig_decoding(panels, savepath):
    padding = 50
    full_width = 1500 + padding
    full_height = 950 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            600 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "C",
            panels["C"],
            20 + padding / 2,
            500 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "D",
            panels["D"],
            920 + padding / 2,
            500 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("grp-combined", "decoding", "std_error.svg"),
        "B": ("grp-combined", "decoding", "std_error_bybin.svg"),
        "C": (
            "grp-combined",
            "decoding",
            "replay_likelihood_bybin.svg",
        ),
    },
    savepath=("figures", "decoding_ppt.svg"),
    copy_to="decoding_ppt.pdf",
)
def fig_decoding_ppt(panels, savepath):
    padding = 50
    full_width = 1500 + padding
    full_height = 950 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            600 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "C",
            panels["C"],
            600 + padding / 2,
            500 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": ("ind-R066d8", "mazes", "maze_matched.svg"),
        "B": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin.svg",
        ),
        "C": (
            "grp-combined",
            "decoding",
            "zscored_logodds_byphase.svg",
        ),
    },
    savepath=("figures", "decoding_logodds_ppt.svg"),
    copy_to="decoding_logodds_ppt.pdf",
)
def fig_decoding_logodds_ppt(panels, savepath):
    padding = 50
    full_width = 1500 + padding
    full_height = 450 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            470 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "C",
            panels["C"],
            950 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "day1": ("grp-day1", "decoding", "zscored_logodds_byphase.svg"),
        "day2": ("grp-day2", "decoding", "zscored_logodds_byphase.svg"),
        "day3": ("grp-day3", "decoding", "zscored_logodds_byphase.svg"),
        "day4": ("grp-day4", "decoding", "zscored_logodds_byphase.svg"),
        "day5": ("grp-day5", "decoding", "zscored_logodds_byphase.svg"),
        "day6": ("grp-day6", "decoding", "zscored_logodds_byphase.svg"),
        "day7": ("grp-day7", "decoding", "zscored_logodds_byphase.svg"),
        "day8": ("grp-day8", "decoding", "zscored_logodds_byphase.svg"),
        "rat1": ("grp-r063", "decoding", "zscored_logodds_byphase.svg"),
        "rat2": ("grp-r066", "decoding", "zscored_logodds_byphase.svg"),
        "rat3": ("grp-r067", "decoding", "zscored_logodds_byphase.svg"),
        "rat4": ("grp-r068", "decoding", "zscored_logodds_byphase.svg"),
    },
    savepath=("figures", "decoding_details.svg"),
    copy_to="decoding_details.pdf",
)
def fig_decoding_details(panels, savepath):
    day_rat_details(panels, savepath)


@task(
    panels={
        "day1": ("grp-day1", "decoding", "zscored_logodds_byphase.svg"),
        "day2": ("grp-day2", "decoding", "zscored_logodds_byphase.svg"),
        "day3": ("grp-day3", "decoding", "zscored_logodds_byphase.svg"),
        "day4": ("grp-day4", "decoding", "zscored_logodds_byphase.svg"),
        "day5": ("grp-day5", "decoding", "zscored_logodds_byphase.svg"),
        "day6": ("grp-day6", "decoding", "zscored_logodds_byphase.svg"),
        "day7": ("grp-day7", "decoding", "zscored_logodds_byphase.svg"),
        "day8": ("grp-day8", "decoding", "zscored_logodds_byphase.svg"),
    },
    savepath=("figures", "decoding_day_details.svg"),
    copy_to="decoding_day_details.pdf",
)
def fig_decoding_day_details(panels, savepath):
    day_details(panels, savepath)


@task(
    panels={
        "rat1": ("grp-r063", "decoding", "zscored_logodds_byphase.svg"),
        "rat2": ("grp-r066", "decoding", "zscored_logodds_byphase.svg"),
        "rat3": ("grp-r067", "decoding", "zscored_logodds_byphase.svg"),
        "rat4": ("grp-r068", "decoding", "zscored_logodds_byphase.svg"),
    },
    savepath=("figures", "decoding_rat_details.svg"),
    copy_to="decoding_rat_details.pdf",
)
def fig_decoding_rat_details(panels, savepath):
    rat_details(panels, savepath)


@task(
    panels={
        "A": ("ind-R066d8", "mazes", "maze_matched.svg"),
        "B": ("grp-combined", "decoding", "replay_decoding_bybin.svg"),
        "C": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin.svg",
        ),
        "D": (
            "grp-combined",
            "replays",
            "exclusive_matched_replays_bybin.svg",
        ),
    },
    savepath=("figures", "decoding_supplemental.svg"),
    copy_to="decoding_supplemental.pdf",
)
def fig_decoding_supplemental(panels, savepath):
    padding = 50
    full_width = 1400 + padding
    full_height = 950 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["A"],
            20 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["B"],
            500 + padding / 2,
            20 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "C",
            panels["C"],
            20 + padding / 2,
            500 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "D",
            panels["D"],
            500 + padding / 2,
            500 + padding / 2,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "prerecord": (
            "grp-combined",
            "decoding",
            "replay_likelihood_bybin_prerecord.svg",
        ),
        "phase1": ("grp-combined", "decoding", "replay_likelihood_bybin_phase1.svg"),
        "pausea": ("grp-combined", "decoding", "replay_likelihood_bybin_pauseA.svg"),
        "phase2": ("grp-combined", "decoding", "replay_likelihood_bybin_phase2.svg"),
        "pauseb": ("grp-combined", "decoding", "replay_likelihood_bybin_pauseB.svg"),
        "phase3": ("grp-combined", "decoding", "replay_likelihood_bybin_phase3.svg"),
        "postrecord": (
            "grp-combined",
            "decoding",
            "replay_likelihood_bybin_postrecord.svg",
        ),
    },
    savepath=("figures", "likelihood_bybin_details.svg"),
    copy_to="likelihood_bybin_details.pdf",
)
def fig_likelihood_bybin_details(panels, savepath):
    padding = 50
    full_width = 2000 + padding
    full_height = 2000 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["prerecord"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["pausea"],
            900 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["pauseb"],
            20 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["postrecord"],
            900 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["phase1"],
            20 + padding,
            1000 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["phase2"],
            900 + padding,
            1000 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["phase3"],
            300 + padding,
            1500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "prerecord": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_prerecord.svg",
        ),
        "phase1": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_phase1.svg",
        ),
        "pausea": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_pauseA.svg",
        ),
        "phase2": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_phase2.svg",
        ),
        "pauseb": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_pauseB.svg",
        ),
        "phase3": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_phase3.svg",
        ),
        "postrecord": (
            "grp-combined",
            "decoding",
            "joined_replay_likelihood_bybin_postrecord.svg",
        ),
    },
    savepath=("figures", "joined_likelihood_bybin_details.svg"),
    copy_to="joined_likelihood_bybin_details.pdf",
)
def fig_joined_likelihood_bybin_details(panels, savepath):
    padding = 50
    full_width = 1800 + padding
    full_height = 1000 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "A",
            panels["prerecord"],
            20 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["pausea"],
            450 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["pauseb"],
            880 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["postrecord"],
            1310 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "B",
            panels["phase1"],
            300 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["phase2"],
            730 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["phase3"],
            1160 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "r063": (
            "ind-R063d7",
            "ind-replays-without-tc",
            "R063d7-swr-u-87-pauseA-without-tc.svg",
        ),
        "r066": (
            "ind-R066d5",
            "ind-replays-without-tc",
            "R066d5-swr-full_shortcut-195-pauseB-without-tc.svg",
        ),
        "r067": (
            "ind-R067d1",
            "ind-replays-without-tc",
            "R067d1-swr-full_shortcut-539-phase3-without-tc.svg",
        ),
        "r068": (
            "ind-R068d8",
            "ind-replays-without-tc",
            "R068d8-swr-full_shortcut-380-pauseB-without-tc.svg",
        ),
    },
    savepath=("figures", "example_swrs.svg"),
    copy_to="example_swrs.pdf",
)
def fig_example_swrs(panels, savepath):
    padding = 50
    full_width = 2000 + padding
    full_height = 400 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            None,
            panels["r063"],
            0 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["r066"],
            500 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["r067"],
            1000 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            None,
            panels["r068"],
            1500 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "r063": (
            "ind-R063d7",
            "ind-replays-without-tc",
            "R063d7-swr-u-87-pauseA-without-tc.svg",
        ),
        "r066": (
            "ind-R066d5",
            "ind-replays-without-tc",
            "R066d5-swr-full_shortcut-195-pauseB-without-tc.svg",
        ),
        "r067": (
            "ind-R067d1",
            "ind-replays-without-tc",
            "R067d1-swr-full_shortcut-539-phase3-without-tc.svg",
        ),
        "r068": (
            "ind-R068d8",
            "ind-replays-without-tc",
            "R068d8-swr-full_shortcut-380-pauseB-without-tc.svg",
        ),
    },
    savepath=("figures", "example_swrs_ppt.svg"),
    copy_to="example_swrs_ppt.pdf",
)
def fig_example_swrs_ppt(panels, savepath):
    padding = 50
    full_width = 1000 + padding
    full_height = 900 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            "R063",
            panels["r063"],
            0 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "R066",
            panels["r066"],
            500 + padding,
            20 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "R067",
            panels["r067"],
            0 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    fig.append(
        el(
            "R068",
            panels["r068"],
            500 + padding,
            500 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


@task(
    panels={
        "A": (
            "ind-R066d5",
            "ind-replays-without-tc",
            "R066d5-swr-full_shortcut-584-phase3-without-tc.svg",
        ),
    },
    savepath=("figures", "example_swr.svg"),
    copy_to="example_swr.pdf",
)
def fig_example_swr(panels, savepath):
    padding = 50
    full_width = 500 + padding
    full_height = 350 + padding

    fig = svgfig(full_width, full_height)
    fig.append(
        el(
            None,
            panels["A"],
            0 + padding,
            0 + padding,
            offset=(-padding / 3, 0),
        )
    )
    savefig(fig, savepath)


def task_combine_tex():
    def combine_tex_files(tex_files, savepath):
        with open(savepath, "w") as outfile:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%", file=outfile)
            print("% AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY %", file=outfile)
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%", file=outfile)

            for path in tex_files:
                with open(path, "r") as infile:
                    print(
                        f"\n%%% {os.path.relpath(path, start=paths.plots_dir)}\n",
                        file=outfile,
                    )
                    outfile.write(infile.read())

    savepath = paths.plot_file("values.tex")
    return {
        "actions": [(combine_tex_files, [Task.tex_files, savepath])],
        "file_dep": Task.tex_files,
        "targets": [savepath],
    }


def task_copy_tex():
    to_copy = [
        # (src, dst)
        (("values.tex",), "values.tex"),
        (("grp-all", "data", "n_neurons.table"), "n_neurons.tex"),
        (("grp-all", "behavior", "n_trials.table"), "n_trials.tex"),
        (("grp-all", "behavior", "n_trials_phase3.table"), "n_trials_phase3.tex"),
        (("grp-all", "swrs", "n_swrs_byphase.table"), "n_swrs_byphase.tex"),
        (("grp-combined", "replays", "n_replays.table"), "n_replays.tex"),
        (("grp-combined", "replays", "percent_replays.table"), "percent_replays.tex"),
    ]
    to_copy = [(paths.plot_file(*src), paths.thesis_tex(dst)) for src, dst in to_copy]

    def copy():
        for src, dst in to_copy:
            shutil.copyfile(src, dst)

    return {
        "actions": [(copy,)],
        "file_dep": [src for src, _ in to_copy],
        "targets": [dst for _, dst in to_copy],
    }


def task_copy_figures():
    figure_files = FigureTask.figure_files

    def svg_to_pdf(svg, pdf):
        if sys.platform == "linux":
            return (
                f'inkscape "{svg}" --export-area-drawing --batch-process '
                f'--export-filename="{pdf}"'
            )
        return rf'"C:\Program Files\Inkscape\inkscape.com" --export-pdf="{pdf}" "{svg}"'

    def svg_to_png(svg, png):
        return rf'"C:\Program Files\Inkscape\inkscape.com" --export-png="{png}" "{svg}"'

    for svg, pdf, png in figure_files:
        yield {
            "name": os.path.basename(svg)[:-4],
            "actions": [svg_to_pdf(svg, pdf), svg_to_png(svg, png)],
            "file_dep": [svg],
            "targets": [pdf, png],
        }
