import colorama
from colorama import Fore, Style

from wrapper.core.treada_io_handler import TreadaSwitcher
from wrapper.config.config_builder import load_config, Config
from wrapper.core.data_management import MtutStageConfiger, ResultBuilder, ResultDataCollector
from wrapper.misc.initializations import init_dirs
from wrapper.states.states_management import StatesMachine, StateStatuses
from wrapper.ui.plotting import TreadaPlotBuilder, AdvancedPlotter


def main():
    config = load_config('config.json')
    init_dirs(paths=config.paths)
    treada_run_loop(config)

    print(f'To complete the program, push the {Fore.GREEN}Enter{Style.RESET_ALL} button. '
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
        if config.flags.dark_result_saving:
            treada.light_off(config.paths.result.temporary.raw)
            # Collect data and build result
            result_build(config, stage_name=config.stages.names.light_off)
        else:
            treada.light_off()

        # Stage 2 - with light
        mtut_stage_configer.light_on(config.stages.light_on)
        treada = TreadaSwitcher(config)
        treada.light_on(config.paths.result.temporary.raw)
        # Collect data and build result
        result_build(config, stage_name=config.stages.names.light_on)

    # Show plot
    if config.flags.plotting.enable:
        AdvancedPlotter.show(block=False)


def result_build(config: Config, stage_name: str):
    # Collect result
    result_collector = ResultDataCollector(mtut_file_path=config.paths.treada_core.mtut,
                                           result_paths=config.paths.result)
    # Set transient parameters
    result_collector.transient.set_window_size_denominator(
        config.advanced_settings.transient.window_size_denominator
    )
    result_collector.transient.set_window_size(config.advanced_settings.transient.window_size)
    # Prepare result
    result_collector.prepare_result_data()

    # Save data in result file and output in console
    result_builder = ResultBuilder(result_collector,
                                   result_paths=config.paths.result,
                                   stage=stage_name)

    # Creation of plot builder object
    plot_builder = TreadaPlotBuilder(result_path=result_builder.result_path,
                                     dist_path=config.paths.result.temporary.distributions,
                                     stage=stage_name,
                                     result_data=result_builder.results,
                                     skip_rows=result_builder.header_length)

    # Display advanced info
    if config.flags.plotting.advanced_info:
        plot_builder.set_advanced_info()
    else:
        plot_builder.set_loaded_info()

    # Save plot to file
    full_plot_path = result_builder.file_name_build(result_path=config.paths.result.plots,
                                                    stage=stage_name,
                                                    file_extension='png')
    plot_builder.save_plot(full_plot_path)


if __name__ == '__main__':
    colorama.init()
    main()
