from wrapper.config.config_builder import Config
from wrapper.core.data_management import ResultDataCollector, ResultBuilder, MtutStageConfiger
from wrapper.ui.plotting import TreadaPlotBuilder
from wrapper.launch.scenarios import scenarios


def call_active_scenario(mtut_stage_configer: MtutStageConfiger, config: Config):
    all_scenario_module_names = dir(scenarios)
    scenario_function_names = [name for name in all_scenario_module_names if callable(getattr(scenarios, name))]

    active_scenario_function = None
    for attr_name in all_scenario_module_names:
        scenario_attr = getattr(scenarios, attr_name)
        if callable(scenario_attr):
            if attr_name.endswith('_scenario') and attr_name == config.scenario.active_name:
                active_scenario_function = scenario_attr
                break
    if active_scenario_function:
        active_scenario_function(mtut_stage_configer, config)
    else:
        raise AttributeError(f'active scenario function with name: "{config.scenario.active_name}" not found')


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
