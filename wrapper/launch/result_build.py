from typing import Union

from wrapper.config.config_build import Config
from wrapper.core.data_management import ResultDataCollector, ResultBuilder
from wrapper.launch.scenarios.scenario_build import Stage
from wrapper.ui.plotting import TreadaPlotBuilder


def transient_result_build(config: Config, stage: Stage, prev_stage_last_current: Union[float, None], relative_time: float):
    # Collect result
    result_collector = ResultDataCollector(mtut_file_path=config.paths.treada_core.mtut,
                                           result_paths=config.paths.result,
                                           relative_time=relative_time)
    # Set transient parameters
    result_collector.transient.set_window_size_denominator(
        config.advanced_settings.transient.window_size_denominator
    )
    result_collector.transient.set_window_size(config.advanced_settings.transient.window_size)
    result_collector.transient.set_criteria_calculating_df_slice(
        config.advanced_settings.transient.criteria_calculating_df_slice
    )
    print(f'{prev_stage_last_current=}')
    # Prepare result
    result_collector.prepare_result_data(stage, prev_stage_last_current)

    # Save data in result file and output in console
    result_builder = ResultBuilder(result_collector,
                                   result_paths=config.paths.result,
                                   result_settings=config.advanced_settings.result,
                                   stage_name=stage.name)

    # Creation of plot builder object
    plot_builder = TreadaPlotBuilder(mtut_path=config.paths.treada_core.mtut,
                                     result_path=result_builder.result_path,
                                     dist_path=config.paths.result.temporary.distributions,
                                     stage_name=stage.name,
                                     runtime_result_data=result_builder.results,
                                     skip_rows=result_builder.header_length)

    # Display advanced info
    if config.flags.plotting.advanced_info:
        plot_builder.set_advanced_info()
    else:
        plot_builder.set_loaded_info()

    # Save plot to file
    full_plot_path = result_builder.file_name_build(result_path=config.paths.result.plots,
                                                    stage_name=stage.name,
                                                    file_extension='png')
    plot_builder.save_plot(full_plot_path)


def capacity_result_build():
    pass

