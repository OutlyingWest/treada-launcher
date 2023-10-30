import os
from dataclasses import is_dataclass
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


def get_from_nested_dataclass(dclass) -> dict:
    """
    Goes through nested dataclass recursively.
    Returns items from the deepest layers of nested branches.
    :param dclass: dataclass object
    :return: dictionary with items from the deepest layers of nested dataclass
    """
    items_dict = {}
    if is_dataclass(dclass):
        for key, value in dclass.__dict__.items():
            if is_dataclass(value):
                nested_items = get_from_nested_dataclass(value)
                items_dict.update(nested_items)
            else:
                items_dict[key] = value
    return items_dict


def set_to_nested_dataclass(dclass, items_dict: dict):
    """
    Goes through nested dataclass recursively.
    Returns items from the deepest layers of nested branches.
    :param dclass: dataclass object
    :param items_dict: dictionary with items which set to the deepest layers of nested dataclass
    """
    if is_dataclass(dclass):
        for key, value in dclass.__dict__.items():
            if is_dataclass(value):
                set_to_nested_dataclass(value, items_dict)
            else:
                dclass.__dict__[key] = items_dict.get(key, value)


def read_line_from_file_end(filename, num_line=1):
    """Returns the num_line before last line of a file (num_line=1 gives last line)"""
    num_newlines = 0
    with open(filename, 'rb') as f:
        try:
            f.seek(-2, os.SEEK_END)
            while num_newlines < num_line:
                f.seek(-2, os.SEEK_CUR)
                if f.read(1) == b'\n':
                    num_newlines += 1
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
    return last_line


if __name__ == '__main__':
    pass
