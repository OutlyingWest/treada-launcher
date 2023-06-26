import os


def create_dir(file_path: str):
    """
    Creates the directory by file_path if it has not existed yet.

    :param file_path:
    :return:
    """
    print(file_path)
    file_path = file_path.rsplit(f'{os.path.sep}', maxsplit=1)[0]
    if not os.path.exists(file_path):
        os.makedirs(file_path)
