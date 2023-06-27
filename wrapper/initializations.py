from wrapper.global_functions import create_dir
from wrapper.config.config_builder import Paths


def init_dirs(paths: Paths):
    create_with_file_set = (
        'udrm'
    )
    for key, file_path in paths.__dict__.items():
        if key in create_with_file_set:
            create_dir(file_path, with_file=True)
        else:
            create_dir(file_path, with_file=False)
