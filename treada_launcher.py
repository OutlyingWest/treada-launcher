import colorama
from colorama import Fore, Style

from wrapper.config.config_builder import load_config, Config
from wrapper import launch
from wrapper.launch.scenarios import scenarios
from wrapper.misc.initializations import init_dirs
from wrapper.core.treada_io_handler import TreadaSwitcher
from wrapper.core.data_management import MtutStageConfiger, ResultBuilder, ResultDataCollector
from wrapper.states.states_management import StatesMachine, StateStatuses
from wrapper.ui.plotting import TreadaPlotBuilder, AdvancedPlotter


def main():
    config = load_config('config.json')
    init_dirs(paths=config.paths)
    treada_running_loop(config)

    print(f'To complete the program, push the {Fore.GREEN}Enter{Style.RESET_ALL} button. '
          f'{Fore.YELLOW}Be careful! All interactive plots will be destroyed.{Style.RESET_ALL}')
    input()


def treada_running_loop(config: Config):
    mtut_stage_configer = MtutStageConfiger(config.paths.treada_core.mtut)
    states_machine = StatesMachine()
    state_statuses = StateStatuses

    running_flag = True
    while running_flag:
        # Updates current machine state in accordance with defined in config treada's modes
        state_status = states_machine.update_state()
        # Check state machine status
        if state_status == state_statuses.END:
            break
        elif state_status == state_statuses.MANUAL:
            running_flag = False

        launch.functions.call_active_scenario(mtut_stage_configer, config)

    # Show plot
    if config.flags.plotting.enable:
        AdvancedPlotter.show(block=False)


if __name__ == '__main__':
    colorama.init()
    main()
