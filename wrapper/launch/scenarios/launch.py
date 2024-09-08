from typing import Callable

from wrapper.launch.scenarios import scenarios
from wrapper.config.config_build import Config
from wrapper.core.data_management import MtutStageConfiger


def call_active_scenario(mtut_stage_configer: MtutStageConfiger, config: Config) -> Callable:
    """
    Call scenario defined in config.json and represented as a function in "scenarios.py" module
    :param mtut_stage_configer: object which provide the interface to manage MTUT file variables
    :param config: dataclass that represents input settings from config.json
    :return: scenario function from scenario's module - "scenarios.py"
    """
    all_scenario_module_names = dir(scenarios)
    active_scenario_function = None
    for attr_name in all_scenario_module_names:
        scenario_attr = getattr(scenarios, attr_name)
        if callable(scenario_attr):
            if attr_name.endswith('_scenario') and attr_name == config.scenario.active_name:
                active_scenario_function = scenario_attr
                break
    if active_scenario_function:
        return active_scenario_function(config, mtut_stage_configer)
    else:
        raise AttributeError(f'active scenario function with name: "{config.scenario.active_name}" is not found')
