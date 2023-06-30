from wrapper.core.io_handler import TreadaSwitcher
from wrapper.config.config_builder import load_config, Config
from wrapper.core.data_management import MtutStageConfiger, ResultBuilder
from wrapper.initializations import init_dirs
from wrapper.states.states_management import StatesMachine, StateStatuses
from wrapper.ui.plotting import plot_builder


def main():
    config = load_config('config.json')
    init_dirs(paths=config.paths)

    treada_run_loop(config)


def treada_run_loop(config: Config):
    mtut_stage_configer = MtutStageConfiger(config.paths.mtut)
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
        treada.light_on(config.paths.treada_raw_output)

        # Save data in result file and output in console
        result_builder = ResultBuilder(mtut_file_path=config.paths.mtut,
                                       treada_raw_output_path=config.paths.treada_raw_output,
                                       result_path=config.paths.treada_result_output)
        result_builder.save_data()
        # Plot result
        if not config.flags.disable_plotting:
            full_plot_path = result_builder.file_name_build(config.paths.plots, file_extension='png')
            plot_builder(result_builder.result_path, full_plot_path)


if __name__ == '__main__':
    main()
