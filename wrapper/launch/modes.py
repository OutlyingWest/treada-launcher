import sys

from colorama import Fore, Style

from wrapper.config.config_builder import Config
from wrapper.launch.scenarios import launch
from wrapper.core.data_management import MtutStageConfiger
from wrapper.states.states_management import StatesMachine, StateStatuses
from wrapper.ui.plotting import AdvancedPlotter


def launcher_mode_selection(config: Config):
    if len(sys.argv) < 2:
        pass
        treada_running_loop(config)
    elif '--plot-res' in sys.argv:
        pass
    elif '--plot-fields-integral' in sys.argv:
        pass
    elif '--collect-distr' in sys.argv:
        pass
    else:
        print('Wrong command line argument.')
        return -1

    print(f'To complete the program, push the {Fore.GREEN}Enter{Style.RESET_ALL} button. '
          f'{Fore.YELLOW}Be careful! All interactive plots will be destroyed.{Style.RESET_ALL}')
    input()


def treada_running_loop(config: Config):
    mtut_stage_configer = MtutStageConfiger(config.paths.treada_core.mtut)
    states_machine = StatesMachine()
    states_machine.flush_state()
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

        launch.call_active_scenario(mtut_stage_configer, config)

    # Show plot
    if config.flags.plotting.enable:
        AdvancedPlotter.show(block=False)
