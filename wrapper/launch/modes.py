import sys
from itertools import chain

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from wrapper.config.config_build import Config
from wrapper.launch.scenarios import launch
from wrapper.core.data_management import MtutStageConfiger
from wrapper.misc.collections.fields_integral.fields_integral_calculation import run_fields_integral_finding
from wrapper.misc.collections.ww_data_collecting.collect_ww_data import run_ww_collecting
from wrapper.states import states
from wrapper.ui.console import quit_user_warning_dialogue, ConsoleUserInteractor
from wrapper.ui.plotting import run_res_plotting
from wrapper.ui.user_interactors import main_console_interactor_create


def launcher_mode_selection(config: Config):
    commands = {
        (): (treada_cli_interaction_loop, config),
        ('--plot-res', '-r'): (run_res_plotting, config),
        ('--plot-fields-integral', '-f'): (run_fields_integral_finding, config),
        ('--collect-distr', '-d'): (run_ww_collecting, config),
    }
    available_commands = '\n'.join([' or short: '.join(command) for command in commands.keys()])
    commands.update({('--help', '-h'): (print, 'Available commands:', available_commands)})
    argv_set = set(sys.argv)
    for command_key in commands:
        if set(command_key) & argv_set or len(argv_set) < 2:
            mode_function, *args = commands[command_key]
            mode_function(*args)
            break
    else:
        print('Wrong command line argument.')
        return -1


def treada_cli_interaction_loop(config: Config):
    user_interactor = main_console_interactor_create(actions=[
        (treada_main_cli, config),
        (sys.exit, ),
    ])
    treada_main_cli(config)
    while True:
        user_interactor.ask_question('new-computation')


def treada_main_cli(config: Config):
    app = QApplication.instance()
    if app is None:
        app = QApplication()
    mtut_stage_configer = MtutStageConfiger(config.paths.treada_core.mtut)
    states_machine = states.BaseStatesMachine(config, state_dataclass=states.BaseState)
    plot_windows = states_machine.run(call_scenario_function=launch.call_active_scenario,
                                      mtut_stage_configer=mtut_stage_configer,
                                      config=config)
    for plot in chain.from_iterable(plot_windows):
        if plot:
            plot.show()
    quit_user_warning_dialogue()
    app.quit()
