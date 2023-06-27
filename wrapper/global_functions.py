import os
from typing import List


def create_dir(file_path: str, with_file=False):
    """
    Creates the directory by file_path if it has not existed yet.

    :param file_path: dir path to create with file name
    :param with_file: If True - creates the file that is included in file_path
    :return:
    """
    dir_path = file_path.rsplit(f'{os.path.sep}', maxsplit=1)[0]
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        if with_file:
            open(file_path, 'w').close()


def create_dirs(dirs: List[list]):
    """
    Creates directories.
    dirs format:
        dirs = [
            [file_path: str, with_file: bool],
            [file_path: str, with_file: bool],
            ...
        ]
    :param dirs: dictionary that contains file paths with file names to create
    :return:
    """
    for directory, with_file in dirs:
        create_dir(directory, with_file)
