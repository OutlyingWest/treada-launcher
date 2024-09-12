from wrapper.config.config_build import Config
from wrapper.core.data_management import MtutManager, find_relative_time
from wrapper.launch.scenarios.scenario_build import load_scenario
from wrapper.misc.global_functions import dict_from_nested_dataclass
from wrapper.ui.plotting import plot_joint_stages_data


def scenario_function(data_class):
    def scenario_decorator_wrapper(scenario_func):
        def scenario_wrapper(config: Config, *args, **kwargs):
            # Load active scenario variables
            scenario = load_scenario(config.paths.scenarios, config.scenario.active_name, data_class)
            # Preserve mtut vars
            mtut_scenario_vars = dict_from_nested_dataclass(scenario.stages)['mtut_vars']
            if not mtut_scenario_vars:
                mtut_scenario_vars = dict()
            mtut_initial_manager = MtutManager(config.paths.treada_core.mtut)
            mtut_initial_manager.load_file()
            # Define relative time
            kwargs['relative_time'] = find_relative_time(mtut_initial_manager)
            mtut_preserved_vars = dict()
            for var in mtut_scenario_vars.keys():
                mtut_preserved_vars[var] = mtut_initial_manager.get_var(var)

            scenario_result = scenario_func(scenario, config, *args, **kwargs)
            # Set scenario result parameters
            if config.plotting.join_stages:
                joint_plot_window = plot_joint_stages_data(scenario,
                                                           config.plotting.join_stages,
                                                           config.paths.treada_core.mtut,
                                                           config.plotting.y_column,
                                                           scenario_result['paths'])
                scenario_result['plots'].append(joint_plot_window)
            # Recover preserved mtut vars
            mtut_after_manager = MtutManager(config.paths.treada_core.mtut)
            mtut_after_manager.load_file()
            for var, value in mtut_preserved_vars.items():
                mtut_after_manager.set_var(var, value)
            mtut_after_manager.save_file()
            return scenario_result
        return scenario_wrapper
    return scenario_decorator_wrapper



