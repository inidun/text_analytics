import os

from penelope.utility import strip_paths


def replace_path(filepath: str, path: str) -> str:
    return os.path.join(path, strip_paths(filepath))
