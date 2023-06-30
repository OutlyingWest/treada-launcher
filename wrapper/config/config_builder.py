"""
Contains features for load settings
"""
import os
import json
from dataclasses import dataclass


@dataclass
class Stages:
    light_off: dict
    light_on: dict


@dataclass
class Paths:
    treada_exe: str
    mtut: str
    treada_raw_output: str
    treada_result_output: str
    current_state: str
    udrm: str
    plots: str


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
        paths=Paths(treada_exe=project_path + config_dict['treada']['paths']['exe'],
                    mtut=project_path + config_dict['treada']['paths']['mtut'],
                    treada_raw_output=project_path + config_dict['treada']['paths']['raw_output'],
                    treada_result_output=project_path + config_dict['treada']['paths']['result_output'],
                    current_state=project_path + config_dict['treada']['paths']['state'],
                    udrm=project_path + config_dict['treada']['paths']['udrm'],
                    plots=project_path + config_dict['treada']['paths']['result_plot'],),
        stages=Stages(light_off=config_dict['treada']['stages']['light_off'],
                      light_on=config_dict['treada']['stages']['light_on'],),
        modes=Modes(udrm_vector_mode=config_dict['treada']['modes']['UDRM_vector_mode'],),
        flags=Flags(disable_plotting=config_dict['treada']['flags']['disable_plotting'],
                    auto_ending=config_dict['treada']['flags']['auto_ending'],),
    )



