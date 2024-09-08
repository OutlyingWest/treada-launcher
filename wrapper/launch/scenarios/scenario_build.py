"""
Contains features to load treada launch scenario
"""
import os.path
import json
from dataclasses import dataclass, field
from typing import Union

from dacite import from_dict


@dataclass
class StageData:
    name: str
    mtut_vars: dict = field(default=None)
    skip_initial_time_step: bool = field(default=False)
    is_capacity_info_collecting: bool = field(default=False)


#############################################
# Dark to light scenario description classes
#############################################
@dataclass
class DarkToLightStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    dark: StageData
    light: StageData


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
    dark_first: StageData
    light: StageData
    dark_second: StageData


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
    turn_off_impulse: StageData
    turn_on_impulse: StageData


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
    capacity_first: StageData
    capacity_second: StageData
    capacity_third: StageData
    capacity_info: StageData


@dataclass
class CapacityScenario:
    stages: CapacityStages


#############################################
# Just light scenario description classes
#############################################
@dataclass
class JustLightStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    light: StageData


@dataclass
class JustLightScenario:
    stages: JustLightStages


#############################################
# Just light with correction scenario description classes
#############################################
@dataclass
class JustLightWithCorrectionStages:
    """
    Info about switching rules for "Treada" work stages.
    """
    light: StageData
    light_correction: StageData


@dataclass
class JustLightWithCorrectionScenario:
    stages: JustLightWithCorrectionStages


def load_scenario(scenarios_path: str,
                  scenario_file_name: str,
                  scenario_dataclass: dataclass) -> dataclass:
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
