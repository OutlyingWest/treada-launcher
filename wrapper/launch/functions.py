from wrapper.config.config_builder import Config
from wrapper.core.data_management import ResultDataCollector, ResultBuilder, MtutStageConfiger, MtutManager
from wrapper.launch.scenarios.scenario_builder import load_scenario
from wrapper.misc.global_functions import get_from_nested_dataclass
from wrapper.ui.plotting import TreadaPlotBuilder
from wrapper.launch.scenarios import scenarios


def call_active_scenario(mtut_stage_configer: MtutStageConfiger, config: Config):
    all_scenario_module_names = dir(scenarios)
    active_scenario_function = None
    for attr_name in all_scenario_module_names:
        scenario_attr = getattr(scenarios, attr_name)
        if callable(scenario_attr):
            if attr_name.endswith('_scenario') and attr_name == config.scenario.active_name:
                active_scenario_function = scenario_attr
                break
    if active_scenario_function:
        active_scenario_function(config, mtut_stage_configer)
    else:
        raise AttributeError(f'active scenario function with name: "{config.scenario.active_name}" not found')


def scenario_function(data_class):
    def scenario_decorator_wrapper(scenario_func):
        def scenario_wrapper(config: Config, *args, **kwargs):
            # Load active scenario variables
            scenario = load_scenario(config.paths.scenarios, config.scenario.active_name, data_class)
            # Preserve mtut vars
            mtut_scenario_vars = get_from_nested_dataclass(scenario.stages)['mtut_vars']
            mtut_initial_manager = MtutManager(config.paths.treada_core.mtut)
            mtut_initial_manager.load_file()
            mtut_preserved_vars = dict()
            for var in mtut_scenario_vars.keys():
                mtut_preserved_vars[var] = mtut_initial_manager.get_var(var)

            result = scenario_func(scenario, config, *args, **kwargs)

            # Recover preserved mtut vars
            mtut_after_manager = MtutManager(config.paths.treada_core.mtut)
            mtut_after_manager.load_file()
            for var, value in mtut_preserved_vars.items():
                mtut_after_manager.set_var(var, value)
            mtut_after_manager.save_file()
            return result
        return scenario_wrapper
    return scenario_decorator_wrapper


def result_build(config: Config, stage_name: str):
    # Collect result
    result_collector = ResultDataCollector(mtut_file_path=config.paths.treada_core.mtut,
                                           result_paths=config.paths.result)
    # Set transient parameters
    result_collector.transient.set_window_size_denominator(
        config.advanced_settings.transient.window_size_denominator
    )
    result_collector.transient.set_window_size(config.advanced_settings.transient.window_size)
    result_collector.transient.set_criteria_calculating_df_slice(
        config.advanced_settings.transient.criteria_calculating_df_slice
    )
    # Prepare result
    result_collector.prepare_result_data()

    # Save data in result file and output in console
    result_builder = ResultBuilder(result_collector,
                                   result_paths=config.paths.result,
                                   stage=stage_name)

    # Creation of plot builder object
    plot_builder = TreadaPlotBuilder(mtut_path=config.paths.treada_core.mtut,
                                     result_path=result_builder.result_path,
                                     dist_path=config.paths.result.temporary.distributions,
                                     stage=stage_name,
                                     runtime_result_data=result_builder.results,
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
