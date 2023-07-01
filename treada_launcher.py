from wrapper.core.io_handler import TreadaSwitcher
from wrapper.config.config_builder import load_config, Config
from wrapper.core.data_management import MtutStageConfiger, ResultBuilder
from wrapper.initializations import init_dirs
from wrapper.states.states_management import StatesMachine, StateStatuses
from wrapper.ui.plotting import TreadaPlotBuilder


def main():
    config = load_config('config.json')
    init_dirs(paths=config.paths)

    treada_run_loop(config)


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
        result_builder.save_data()
        # Plot result
        # if not config.flags.disable_plotting:
        #     full_plot_path = result_builder.file_name_build(config.paths.output.plots, file_extension='png')


        # plot_builder(result_builder.result_path,
        #              plot_path=full_plot_path,
        #              special_points=[(transient_time_value, ending_current_density)],
        #              points_annotation=f"Transient time = {transient_time_value:.3f}")

        # Collection of data to display on plot
        transient_time_value = result_builder.results['transient_time']
        ending_current_density = result_builder.results['ending_current_density']
        # Creation of plot builder object
        plot_builder = TreadaPlotBuilder(result_path=result_builder.result_path,
                                         ending_point_coords=(transient_time_value, ending_current_density),
                                         transient_time=transient_time_value)

        # Save plot to file
        full_plot_path = result_builder.file_name_build(config.paths.output.plots, file_extension='png')
        plot_builder.save_plot(full_plot_path)
        # Show plot
        if not config.flags.disable_plotting:
            plot_builder.show()


if __name__ == '__main__':
    main()
