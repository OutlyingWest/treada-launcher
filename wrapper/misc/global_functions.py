import os
import shutil
from dataclasses import is_dataclass


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


def dict_from_nested_dataclass(dclass) -> dict:
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
                nested_items = dict_from_nested_dataclass(value)
                items_dict.update(nested_items)
            else:
                items_dict[key] = value
    return items_dict


def dict_to_nested_dataclass(dclass, items_dict: dict):
    """
    Goes through nested dataclass recursively.
    Returns items from the deepest layers of nested branches.
    :param dclass: dataclass object
    :param items_dict: dictionary with items which set to the deepest layers of nested dataclass
    """
    if is_dataclass(dclass):
        for key, value in dclass.__dict__.items():
            if is_dataclass(value):
                dict_to_nested_dataclass(value, items_dict)
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


def create_dirs(paths, with_file=tuple()):
    paths_dict = dict_from_nested_dataclass(paths)
    for key, file_path in paths_dict.items():
        if key in with_file:
            create_dir(file_path, with_file=True)
        else:
            create_dir(file_path, with_file=False)


def remove_dirs(paths):
    """
    Remove multiple directories recursively
    :param paths: list of str or dataclass
    :return:
    """
    if not isinstance(paths, list):
        paths_dict = dict_from_nested_dataclass(paths)
        paths_list = [path for path in paths_dict.values()]
        paths = paths_list
    [shutil.rmtree(path) for path in paths]


if __name__ == '__main__':
    pass
