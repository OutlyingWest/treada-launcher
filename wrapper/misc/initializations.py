from wrapper.misc.global_functions import create_dir, get_from_nested_dataclass
from wrapper.config.config_builder import Paths


def init_dirs(paths: Paths):
    create_with_file = (
        'udrm',
    )
    paths_dict = get_from_nested_dataclass(paths)
    for key, file_path in paths_dict.items():
        if key in create_with_file:
            create_dir(file_path, with_file=True)
        else:
            create_dir(file_path, with_file=False)



