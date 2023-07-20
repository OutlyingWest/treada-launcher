import time

import colorama
from colorama import Fore, Style

from wrapper.core.treada_io_handler import TreadaSwitcher
from wrapper.config.config_builder import load_config, Config
from wrapper.core.data_management import MtutStageConfiger, ResultBuilder
from wrapper.initializations import init_dirs
from wrapper.states.states_management import StatesMachine, StateStatuses
from wrapper.ui.plotting import TreadaPlotBuilder, AdvancedPlotter


def main():
    config = load_config('config.json')
    init_dirs(paths=config.paths)

    treada_run_loop(config)

    print(f'To complete the program, click the {Fore.GREEN}Enter{Style.RESET_ALL} button. '
          f'{Fore.YELLOW}Be careful! All interactive plots will be destroyed.{Style.RESET_ALL}')
    input()


def treada_run_loop(config: Config):
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

        # Stage 1 - without light
        mtut_stage_configer.light_off(config.stages.light_off)
        treada = TreadaSwitcher(config)
        treada.light_off()

        # Stage 2 - with light
        mtut_stage_configer.light_on(config.stages.light_on)
        treada = TreadaSwitcher(config)
        treada.light_on(config.paths.output.raw)

        # Save data in result file and output in console
        result_builder = ResultBuilder(mtut_file_path=config.paths.treada_core.mtut,
                                       treada_raw_output_path=config.paths.output.raw,
                                       result_path=config.paths.output.result)

        # Creation of plot builder object
        plot_builder = TreadaPlotBuilder(result_path=result_builder.result_path,
                                         result_data=result_builder.results)

        # Display advanced info
        if config.flags.plotting.advanced_info:
            plot_builder.set_advanced_info()

        # Save plot to file
        full_plot_path = result_builder.file_name_build(config.paths.output.plots, file_extension='png')
        plot_builder.save_plot(full_plot_path)

    # Show plot
    if config.flags.plotting.enable:
        AdvancedPlotter.show(block=False)


def wait_interrupt():
    try:
        while True:
            time.sleep(0.5)
            pass
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    colorama.init()
    main()
