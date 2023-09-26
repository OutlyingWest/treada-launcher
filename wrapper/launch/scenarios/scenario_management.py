from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutManager
from wrapper.launch.scenarios.scenario_builder import load_scenario
from wrapper.misc.global_functions import get_from_nested_dataclass


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