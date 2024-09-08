import sys
from itertools import chain

from PySide6.QtWidgets import QApplication

from wrapper.config.config_build import Config
from wrapper.launch.scenarios import launch
from wrapper.core.data_management import MtutStageConfiger
from wrapper.misc.collections.fields_integral.fields_integral_calculation import run_fields_integral_finding
from wrapper.misc.collections.ww_data_collecting.collect_ww_data import run_ww_collecting
from wrapper.states import states
from wrapper.ui.console import quit_user_warning_dialogue
from wrapper.ui.plotting import run_res_plotting


def launcher_mode_selection(config: Config):
    argv_set = set(sys.argv)
    if len(sys.argv) < 2:
        treada_main_cli(config)
    elif {'--plot-res', '-r'} & argv_set:
        run_res_plotting(config)
    elif {'--plot-fields-integral', '-f'} & argv_set:
        run_fields_integral_finding(config)
    elif {'--collect-distr', '-d'} & argv_set:
        run_ww_collecting(config)
    else:
        print('Wrong command line argument.')
        return -1


def treada_main_cli(config: Config):
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

