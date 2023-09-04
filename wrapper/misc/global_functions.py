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


if __name__ == '__main__':
    pass
