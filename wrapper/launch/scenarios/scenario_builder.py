"""
Contains features to load treada launch scenario
"""
import os.path
import json
from dataclasses import dataclass, field
from typing import Union

from dacite import from_dict

from wrapper.config.config_builder import Config


@dataclass
class Stage:
    name: str
    mtut_vars: dict
    skip_initial_time_step: bool = field(default=False)


#############################################
# Dark to light scenario description classes
#############################################
@dataclass
class DarkToLightStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    dark: Stage
    light: Stage


@dataclass
class DarkToLightScenario:
    stages: DarkToLightStages


#####################################################
# Dark -> light -> dark scenario description classes
#####################################################
@dataclass
class DarkLightDarkStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    dark_first: Stage
    light: Stage
    dark_second: Stage


@dataclass
class DarkLightDarkScenario:
    stages: DarkLightDarkStages


########################################################
# Turn-on diode in the dark scenario description classes
########################################################
@dataclass
class TurnOnImpulseDarkStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    turn_off_impulse: Stage
    turn_on_impulse: Stage


@dataclass
class TurnOnImpulseDarkScenario:
    stages: TurnOnImpulseDarkStages


########################################################
# Capacity
########################################################
@dataclass
class CapacityStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    first_transient: Stage
    second_transient: Stage
    third_transient: Stage
    info_collecting: Stage


@dataclass
class CapacityScenario:
    stages: CapacityStages


def load_scenario(scenarios_path: str,
                  scenario_file_name: str,
                  scenario_dataclass: dataclass) -> Union[DarkToLightScenario,
                                                          DarkLightDarkScenario,
                                                          TurnOnImpulseDarkScenario]:
    """
    Returns scenario dataclass
    :param scenarios_path: path to scenarios folder
    :param scenario_file_name: name of scenario file excludes extension
    :param scenario_dataclass: dataclass for scenario
    :return: scenario dataclass
    """
    full_scenario_path = os.path.join(scenarios_path, f'{scenario_file_name}.json')

    with open(full_scenario_path, "r") as scenario_file:
        scenario_dict = json.load(scenario_file)

    scenario = from_dict(data_class=scenario_dataclass, data=scenario_dict)
    return scenario
