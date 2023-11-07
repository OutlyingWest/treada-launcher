import colorama

from wrapper.config.config_builder import load_config
from wrapper.launch.modes import launcher_mode_selection
from wrapper.misc.initializations import init_dirs


def main():
    config = load_config('config.json')
    init_dirs(paths=config.paths, is_remove_distributions=config.flags.remove_old_distributions)
    launcher_mode_selection(config)


if __name__ == '__main__':
    colorama.init()
    main()
