"""Convenience classes to reduce boilerplate and automatically load/save from cache."""

import os
from inspect import getfullargspec
from keyword import iskeyword

import cache
import paths


def _ensure_varname_list(value, name):
    def assert_valid_varname(varname):
        assert varname.isidentifier() and not iskeyword(
            varname
        ), f"'{varname}' is not a valid variable name"

    if value is None:
        return []

    if isinstance(value, str):
        assert_valid_varname(value)
        return [value]

    assert isinstance(value, list), f"'{name}' must be a string or list of strings"
    for varname in value:
        assert_valid_varname(varname)
    return value


class Task:
    tex_files = []

    def __init__(self, function, savepath=None):
        self.function = function
        self.cache_loads = getfullargspec(self.function).kwonlyargs
        if "savepath" in self.cache_loads:
            self.cache_loads.remove("savepath")
        if "example_plots" in self.cache_loads:
            self.cache_loads.remove("example_plots")

        self.savepath = savepath
        assert self.savepath is None or isinstance(
            self.savepath, (tuple, dict)
        ), f"'savepath' must be a tuple or dict (got {type(savepath).__name__}"

        self.create_doit_tasks.__func__.__doc__ = function.__doc__

    def create_doit_tasks(self):
        raise NotImplementedError("Subclasses must implement")

    def _format_savepath(self, mkdir=False, **fmt_args):
        def tuple_to_path(args):
            if "info" in fmt_args:
                assert "group_name" not in fmt_args
                args = ("ind-{info.session_id}",) + args
            if "group_name" in fmt_args:
                assert "info" not in fmt_args
                args = ("grp-{group_name}",) + args
            path = paths.plot_file(*(arg.format(**fmt_args) for arg in args))
            if mkdir:
                os.makedirs(os.path.dirname(path), exist_ok=True)
            return path

        def is_tex_file(path):
            return path.endswith(".tex") and not mkdir

        if isinstance(self.savepath, tuple):
            savepath = tuple_to_path(self.savepath)
            if is_tex_file(savepath):
                Task.tex_files.append(savepath)
            return savepath

        if isinstance(self.savepath, dict):
            savepaths = {k: tuple_to_path(v) for k, v in self.savepath.items()}
            for savepath in savepaths.values():
                if is_tex_file(savepath):
                    Task.tex_files.append(savepath)
            return savepaths
        assert self.savepath is None, "'savepath' must be None, tuple or {str: tuple}"


class ExamplePlots:
    def __init__(self, argnames, savepath, plots):
        self.argnames = argnames
        self._savepath = savepath
        self.plots = plots

    def savepath(self, info, *args, mkdir=True):
        fmt_args = dict(zip(self.argnames, args))
        savepath = paths.plot_file(
            *(arg.format(info=info, **fmt_args) for arg in self._savepath)
        )
        if mkdir:
            os.makedirs(os.path.dirname(savepath), exist_ok=True)
        return savepath

    def zip(self, info, mkdir=True):
        for args in self.plots.get(info.session_id, []):
            yield args + tuple([self.savepath(info, *args, mkdir=mkdir)])


class InfoTask(Task):
    def __init__(
        self,
        function,
        infos,
        cache_saves=None,
        read_example_plots=None,
        write_example_plots=None,
        savepath=None,
    ):
        assert isinstance(infos, list)
        assert len(infos) > 0
        self.infos = infos
        self.cache_saves = _ensure_varname_list(cache_saves, "cache_saves")
        self.read_example_plots = _ensure_varname_list(
            read_example_plots, "read_example_plots"
        )
        self.write_example_plots = _ensure_varname_list(
            write_example_plots, "write_example_plots"
        )
        super().__init__(function=function, savepath=savepath)

    def __call__(self, info, **kwargs):
        loaded = {
            key: cache.load(f"ind-{info.session_id}", key)
            for key in self.cache_loads
            if key not in kwargs
        }
        kwargs.update(loaded)
        if self.savepath is not None and "savepath" not in kwargs:
            kwargs["savepath"] = self._format_savepath(info=info, mkdir=True)
        ex_plots = self.read_example_plots + self.write_example_plots
        if len(ex_plots) > 0:
            kwargs["example_plots"] = {key: example_plots[key] for key in ex_plots}
        retval = self.function(info, **kwargs)
        if len(self.cache_saves) == 0:
            assert retval is None
        elif len(self.cache_saves) == 1:
            cache.save(f"ind-{info.session_id}", self.cache_saves[0], retval)
        else:
            assert isinstance(retval, dict)
            for key in self.cache_saves:
                cache.save(f"ind-{info.session_id}", key, retval[key])

    def _file_dep(self, info):
        file_dep = [info.path]
        file_dep.extend(
            paths.cached_file(f"ind-{info.session_id}", key=key)
            for key in self.cache_loads
        )
        for key in self.read_example_plots:
            file_dep.extend(
                zipped[-1] for zipped in example_plots[key].zip(info, mkdir=False)
            )
        return file_dep

    def _targets(self, info):
        targets = []
        if isinstance(self.savepath, tuple):
            targets.append(self._format_savepath(info=info))
        elif isinstance(self.savepath, dict):
            targets.extend(self._format_savepath(info=info).values())
        targets.extend(
            paths.cached_file(f"ind-{info.session_id}", key=key)
            for key in self.cache_saves
        )
        for key in self.write_example_plots:
            targets.extend(
                zipped[-1] for zipped in example_plots[key].zip(info, mkdir=False)
            )
        return targets

    def create_doit_tasks(self):
        for info in self.infos:
            yield {
                "basename": self.function.__name__,
                "name": info.session_id,
                "actions": [(self.__call__, [info])],
                "file_dep": self._file_dep(info),
                "targets": self._targets(info),
            }


class GroupTask(Task):
    def __init__(
        self,
        function,
        groups,
        cache_saves=None,
        savepath=None,
    ):
        assert isinstance(groups, dict)
        assert len(groups) > 0
        self.groups = groups
        self.cache_saves = _ensure_varname_list(cache_saves, "cache_saves")
        super().__init__(function=function, savepath=savepath)

    def __call__(self, infos, group_name, **kwargs):
        loaded = {
            key: (
                [
                    cache.load(f"ind-{info.session_id}", key[len("all_") :])
                    for info in infos
                ]
                if key.startswith("all_")
                else cache.load(f"grp-{group_name}", key)
            )
            for key in self.cache_loads
            if key not in kwargs
        }
        kwargs.update(loaded)
        if self.savepath is not None and "savepath" not in kwargs:
            kwargs["savepath"] = self._format_savepath(
                infos=infos, group_name=group_name, mkdir=True
            )
        retval = self.function(infos, group_name, **kwargs)
        if len(self.cache_saves) == 0:
            assert retval is None
        elif len(self.cache_saves) == 1:
            cache.save(f"grp-{group_name}", self.cache_saves[0], retval)
        else:
            assert isinstance(retval, dict)
            for key in self.cache_saves:
                cache.save(f"grp-{group_name}", key, retval[key])

    def _file_dep(self, infos, group_name):
        file_dep = []

        if any(key.startswith("all_") for key in self.cache_loads):
            for info in infos:
                file_dep.append(info.path)

        for key in self.cache_loads:
            if key.startswith("all_"):
                file_dep.extend(
                    paths.cached_file(f"ind-{info.session_id}", key=key[len("all_") :])
                    for info in infos
                )
            else:
                file_dep.append(paths.cached_file(f"grp-{group_name}", key=key))

        return file_dep

    def _targets(self, infos, group_name):
        targets = []
        if isinstance(self.savepath, tuple):
            targets.append(self._format_savepath(infos=infos, group_name=group_name))
        elif isinstance(self.savepath, dict):
            targets.extend(
                self._format_savepath(infos=infos, group_name=group_name).values()
            )
        targets.extend(
            paths.cached_file(f"grp-{group_name}", key=key) for key in self.cache_saves
        )
        return targets

    def create_doit_tasks(self):
        for group_name, infos in self.groups.items():
            yield {
                "basename": self.function.__name__,
                "name": group_name,
                "actions": [(self.__call__, [infos, group_name])],
                "file_dep": self._file_dep(infos, group_name),
                "targets": self._targets(infos, group_name),
            }


class FigureTask(Task):
    figure_files = []  # All the savepaths for these tasks

    def __init__(self, function, panels, copy_to, savepath):
        assert savepath is not None
        self.panels = {
            key: paths.plot_file(*pathargs) for key, pathargs in panels.items()
        }
        self.copy_to = copy_to
        super().__init__(function, savepath)

    def __call__(self, **kwargs):
        if self.savepath is not None and "savepath" not in kwargs:
            kwargs["savepath"] = self._format_savepath(mkdir=True)
        self.function(panels=self.panels, **kwargs)

    def create_doit_tasks(self):
        target = self._format_savepath()
        assert isinstance(target, str)
        FigureTask.figure_files.append((target, paths.thesis_image(self.copy_to)))

        return {
            "basename": self.function.__name__,
            "actions": [(self.__call__, [])],
            "file_dep": list(self.panels.values()),
            "targets": [target],
        }


def task(
    *,
    infos=None,
    groups=None,
    read_example_plots=None,
    write_example_plots=None,
    panels=None,
    cache_saves=None,
    savepath=None,
    copy_to=None,
):
    def decorator(function):
        if infos is not None:
            assert groups is None and panels is None and copy_to is None
        elif groups is not None:
            assert infos is None and panels is None and copy_to is None
            assert read_example_plots is None
            assert write_example_plots is None
        elif panels is not None:
            assert infos is None and groups is None and copy_to is not None
            assert copy_to.endswith(".pdf")
            assert read_example_plots is None
            assert write_example_plots is None
        else:
            assert False

        if infos is not None:
            return InfoTask(
                function,
                infos,
                cache_saves=cache_saves,
                read_example_plots=read_example_plots,
                write_example_plots=write_example_plots,
                savepath=savepath,
            )
        elif groups is not None:
            return GroupTask(
                function, groups, cache_saves=cache_saves, savepath=savepath
            )
        return FigureTask(function, panels, copy_to, savepath=savepath)

    return decorator


example_plots = {
    "matched_run_raster": ExamplePlots(
        argnames=["trajectory", "i"],
        savepath=(
            "ind-{info.session_id}",
            "ind-matched-run-rasters",
            "matched_run_rasters_{trajectory}_{i}.svg",
        ),
        plots={},
    ),
    "run_raster": ExamplePlots(
        argnames=["trajectory", "i"],
        savepath=(
            "ind-{info.session_id}",
            "ind-run-rasters",
            "run_raster_{trajectory}_{i}.svg",
        ),
        plots={},
    ),
    "swrs": ExamplePlots(
        argnames=["trajectory", "i", "task_time", "type"],
        savepath=(
            "ind-{info.session_id}",
            "ind-{type}",
            "{info.session_id}-swr-{trajectory}-{i}-{task_time}.svg",
        ),
        plots={
            "R063d7": [
                ("full_shortcut", 153, "pauseA", "replays"),
                ("full_shortcut", 980, "phase3", "replays"),
                ("u", 113, "pauseA", "replays"),
            ],
            "R066d5": [
                ("u", 339, "pauseB", "replays"),
                ("full_shortcut", 195, "pauseB", "replays"),
            ],
            "R067d1": [
                ("full_shortcut", 486, "phase3", "replays"),
                ("full_shortcut", 508, "phase3", "replays"),
                ("full_shortcut", 539, "phase3", "replays"),
            ],
            "R068d8": [("u", 601, "phase3", "replays")],
        },
    ),
    "swrs_without_tc": ExamplePlots(
        argnames=["trajectory", "i", "task_time", "type"],
        savepath=(
            "ind-{info.session_id}",
            "ind-{type}",
            "{info.session_id}-swr-{trajectory}-{i}-{task_time}-without-tc.svg",
        ),
        plots={
            "R063d7": [
                ("u", 686, "pauseB", "replays-without-tc"),
                ("u", 87, "pauseA", "replays-without-tc"),
            ],
            "R066d5": [
                ("u", 339, "pauseB", "replays-without-tc"),
                ("full_shortcut", 195, "pauseB", "replays-without-tc"),
                ("full_shortcut", 584, "phase3", "replays-without-tc"),
            ],
            "R067d1": [
                ("full_shortcut", 539, "phase3", "replays-without-tc"),
            ],
            "R068d8": [
                ("u", 601, "phase3", "replays-without-tc"),
                ("full_shortcut", 380, "pauseB", "replays-without-tc"),
            ],
        },
    ),
}
