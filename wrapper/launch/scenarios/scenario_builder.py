"""
Contains features to load treada launch scenario
"""
import os.path
import json
from dataclasses import dataclass
from typing import Union

from dacite import from_dict


@dataclass
class Stage:
    name: str
    mtut_vars: dict


#############################################
# Dark to light scenario description classes
#############################################
@dataclass
class DarkToLightStages:
    dark: Stage
    light: Stage


@dataclass
class DarkToLightScenario:
    """
    Info about switching rules for "Treada" work stages.
    """
    stages: DarkToLightStages


#####################################################
# Dark -> light -> dark scenario description classes
#####################################################
@dataclass
class DarkLightDarkStages:
    dark_first: Stage
    light: Stage
    dark_second: Stage


@dataclass
class DarkLightDarkScenario:
    """
    Info about switching rules for "Treada" work stages.
    """
    stages: DarkLightDarkStages


def load_scenario(scenarios_path: str, scenario_file_name: str) -> dataclass:
    """
    Returns scenario dataclass
    :param scenarios_path: path to scenarios folder
    :param scenario_file_name: name of scenario file includes extension
    :return: scenario dataclass
    """
    allowed_scenarios = {
        'dark_to_light_scenario.json': DarkToLightScenario,
        'dark_light_dark_scenario.json': DarkLightDarkScenario,
    }
    full_scenario_path = os.path.join(scenarios_path, scenario_file_name)

    with open(full_scenario_path, "r") as scenario_file:
        scenario_dict = json.load(scenario_file)

    scenario = from_dict(data_class=allowed_scenarios[scenario_file_name], data=scenario_dict)
    return scenario




