import os

from wrapper.misc.global_functions import create_dirs, remove_dirs
from wrapper.config.config_builder import Paths


def init_dirs(paths: Paths, is_remove_distributions: bool):
    create_dirs(paths, with_file=('udrm',))
    if is_remove_distributions:
        to_remove_dirs_iter = os.scandir(paths.result.temporary.distributions)
        remove_dirs([to_remove_dir.path for to_remove_dir in to_remove_dirs_iter])





