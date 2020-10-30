import os
import sys
from importlib import import_module
from timeit import default_timer

import doit
import matplotlib
from doit.reporter import ConsoleReporter

from tasks import Task

if sys.platform == "linux":
    os.environ["R_LIBS_SITE"] = "/usr/lib/R/site-library"

matplotlib.use("Agg")


class Timer:
    def __init__(self, task):
        self.task = task
        self._start = None
        self.duration = 0.0

    def start(self):
        self._start = default_timer()

    def finish(self):
        if self._start is not None:
            self.duration = default_timer() - self._start
            self._start = None


class TimedConsoleReporter(ConsoleReporter):
    def __init__(self, outstream, options):
        super().__init__(outstream, options)
        self.timers = {}

    def get_status(self, task):
        self.timers[task.name] = Timer(task)

    def execute_task(self, task):
        self.timers[task.name].start()
        super().execute_task(task)

    def add_failure(self, task, exception):
        self.timers[task.name].finish()
        self.write("X  %.3fs %s\n" % (self.timers[task.name].duration, task.title()))
        super().add_failure(task, exception)

    def add_success(self, task):
        self.timers[task.name].finish()
        self.write("O  %.3fs %s\n" % (self.timers[task.name].duration, task.title()))
        super().add_success(task)


DOIT_CONFIG = {
    "check_file_uptodate": "timestamp",
    "num_process": 6 if sys.platform == "linux" else 3,
    "reporter": TimedConsoleReporter,
    "verbosity": 2,
}


def find_tasks(module_name):
    module = import_module(module_name)
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Task) or name.startswith("task_"):
            globals()[name] = obj


find_tasks("analyze_data")
find_tasks("plot_data")
find_tasks("analyze_decoding")
find_tasks("plot_decoding")
find_tasks("analyze_linear")
find_tasks("plot_linear")
find_tasks("analyze_position")
find_tasks("plot_position")
find_tasks("analyze_swrs")
find_tasks("plot_swrs")
find_tasks("analyze_trials")
find_tasks("plot_trials")
find_tasks("analyze_tuning_curves")
find_tasks("plot_tuning_curves")
find_tasks("combine")  # make sure this is loaded last


if __name__ == "__main__":
    doit.run(globals())
