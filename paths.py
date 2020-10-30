import os

code_dir = os.path.dirname(os.path.realpath(__file__))
if os.name == "posix":
    root = "/media/emily/Seagate Backup Plus Drive/phd-thesis"
else:
    root = code_dir

data_dir = os.path.abspath(os.path.join(root, "data"))
cache_dir = os.path.abspath(os.path.join(root, "cache"))
plots_dir = os.path.abspath(os.path.join(root, "plots"))
info_dir = os.path.abspath(os.path.join(code_dir, "info"))
thesis_dir = os.path.abspath(os.path.join(code_dir, os.pardir, "thesis"))


def recording_dir(info):
    return os.path.join(data_dir, info.rat_id, f"{info.session}_recording")


def position_file(info):
    return os.path.join(recording_dir(info), f"{info.session}-VT1.nvt")


def event_file(info):
    return os.path.join(recording_dir(info), f"{info.session}-Events.nev")


def lfp_swr_file(info):
    return os.path.join(
        recording_dir(info), f"{info.session}-{info.lfp_swr_suffix}.ncs"
    )


def lfp_theta_file(info):
    return os.path.join(
        recording_dir(info), f"{info.session}-{info.lfp_theta_suffix}.ncs"
    )


def swr_file(info):
    return os.path.join(recording_dir(info), f"{info.session}-SWRcandidates-ext.mat")


def position_csv_file(info):
    return os.path.join(
        cache_dir, f"ind-{info.session_id}", f"{info.session}-position.csv"
    )


def cached_file(group, key):
    assert isinstance(key, str)
    return os.path.join(cache_dir, group, f"{key}.pkl")


def plot_file(*path_args):
    path = os.path.join(plots_dir, *path_args)
    return path


def thesis_image(filename):
    return os.path.join(thesis_dir, "images", filename)


def thesis_tex(filename):
    return os.path.join(thesis_dir, "generated", filename)


def plot_dir(*path_args, mkdir=False):
    path = os.path.join(plots_dir, *path_args)
    if mkdir:
        os.makedirs(path, exist_ok=True)
    return path
