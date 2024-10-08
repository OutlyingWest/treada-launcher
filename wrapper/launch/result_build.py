from typing import Union
from logging import Logger

from wrapper.config.config_build import Config
from wrapper.core.data_management import (
    TransientResultDataCollector, TransientResultBuilder, SmallSignalResultBuilder
)
from wrapper.launch.scenarios.scenario_build import StageData
from wrapper.ui.plotting import TransientPlotBuilder, ImpedancePlotBuilder


def transient_result_build(config: Config, stage: StageData, prev_stage_last_current: Union[float, None],
                           relative_time: float):
    # Collect result
    result_collector = TransientResultDataCollector(mtut_file_path=config.paths.treada_core.mtut,
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
    result_collector.prepare_result_data(stage,
                                         prev_stage_last_current,
                                         config.advanced_settings.result.dataframe.custom)

    # Save transient_result in result file and output in console
    result_builder = TransientResultBuilder(result_collector,
                                            result_paths=config.paths.result,
                                            result_settings=config.advanced_settings.result,
                                            stage_name=stage.name)

    if config.plotting.enable:
        # Creation of plot builder object
        plot_builder = TransientPlotBuilder(mtut_path=config.paths.treada_core.mtut,
                                            result_path=result_builder.result_path,
                                            dist_path=config.paths.result.temporary.distributions,
                                            stage_name=stage.name,
                                            runtime_result_data=result_builder.results,
                                            skip_rows=result_builder.header_length,
                                            y_transient_col_key=config.plotting.y_column,
                                            is_transient_ending_point=False)

        # Display advanced info
        if config.plotting.advanced_info:
            plot_builder.set_advanced_info()
        else:
            plot_builder.set_loaded_info()

        # Save plot to file
        full_plot_path = result_builder.file_path_with_name_build(result_path=config.paths.result.plots,
                                                                  stage_name=stage.name,
                                                                  file_extension='png')
        plot_builder.save_plot(full_plot_path)
        return plot_builder.plot_window, result_builder.result_path


def impedance_result_build(config: Config, stage: StageData, is_repeated: bool):
    result_builder = SmallSignalResultBuilder(result_paths=config.paths.result, stage_name=stage.name,
                                              is_repeated_stage=is_repeated)
    plot_builder = ImpedancePlotBuilder(result_path=result_builder.result_path)
    plot_builder.show()
