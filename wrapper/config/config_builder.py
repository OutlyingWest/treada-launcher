"""
Contains features for load configuration
"""
import os
import json
from dataclasses import dataclass


@dataclass
class Stages:
    light_off: dict
    light_on: dict


# Paths section
@dataclass
class TreadaCorePaths:
    exe: str
    mtut: str


@dataclass
class InputPaths:
    udrm: str
    current_state: str


@dataclass
class OutputPaths:
    raw: str
    result: str
    plots: str


@dataclass
class Paths:
    treada_core: TreadaCorePaths
    input: InputPaths
    output: OutputPaths


@dataclass
class Modes:
    udrm_vector_mode: bool


@dataclass
class Flags:
    disable_plotting: bool
    auto_ending: bool


@dataclass
class Config:
    paths: Paths
    stages: Stages
    modes: Modes
    flags: Flags


def load_config(config_name: str = None):
    script_path = os.path.dirname((os.path.abspath(__file__)))
    project_path = script_path.rsplit(sep=os.path.sep, maxsplit=2)[0] + os.path.sep
    full_config_path = os.path.sep.join([script_path, config_name])

    with open(full_config_path, "r") as config_file:
        config_dict = json.load(config_file)
    # load configuration from file
    return Config(
        paths=Paths(
            treada_core=TreadaCorePaths(
                exe=project_path + config_dict['paths']['treada_core']['exe'],
                mtut=project_path + config_dict['paths']['treada_core']['mtut'],
            ),
            input=InputPaths(
                udrm=project_path + config_dict['paths']['input']['udrm'],
                current_state=project_path + config_dict['paths']['input']['state'],
            ),
            output=OutputPaths(
                raw=project_path + config_dict['paths']['output']['raw'],
                result=project_path + config_dict['paths']['output']['results'],
                plots=project_path + config_dict['paths']['output']['plots'],
            ),
        ),
        stages=Stages(light_off=config_dict['stages']['light_off'],
                      light_on=config_dict['stages']['light_on'],),
        modes=Modes(udrm_vector_mode=config_dict['modes']['UDRM_vector_mode'],),
        flags=Flags(disable_plotting=config_dict['flags']['disable_plotting'],
                    auto_ending=config_dict['flags']['auto_ending'],),
    )



