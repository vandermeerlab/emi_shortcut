"""Helper functions for loading / saving items to paths.cache_dir"""

import os
import pickle

import paths


def load(group, key):
    cached_file = paths.cached_file(group, key)
    assert os.path.exists(
        cached_file
    ), f"'{cached_file}' does not exist. Cache it first."

    with open(cached_file, "rb") as fileobj:
        return pickle.load(fileobj)


def save(group, key, obj):
    cached_file = paths.cached_file(group, key)
    os.makedirs(os.path.dirname(cached_file), exist_ok=True)
    with open(cached_file, "wb") as fileobj:
        pickle.dump(obj, fileobj)
    print("Saved {}".format(cached_file))
