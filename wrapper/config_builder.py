"""
Contains features for load settings
"""
import os
import json
from dataclasses import dataclass


@dataclass()
class Stages:
    light_off: dict
    light_on: dict


@dataclass()
class Paths:
    treada_exe: str
    mtut: str
    treada_raw_output: str


@dataclass
class Config:
    paths: Paths
    stages: Stages


def load_config(config_path: str = None):
    script_path = os.path.dirname((os.path.abspath(__file__)))
    project_path = os.path.split(script_path)[0] + '\\'
    full_config_path = project_path + config_path

    with open(full_config_path, "r") as config_file:
        config_dict = json.load(config_file)
    # load configuration from file
    return Config(
        paths=Paths(treada_exe=project_path + config_dict['treada']['paths']['to_exe'],
                    mtut=project_path + config_dict['treada']['paths']['to_mtut'],
                    treada_raw_output=project_path + config_dict['treada']['paths']['to_raw_output']),

        stages=Stages(light_off=config_dict['treada']['stages']['light_off'],
                      light_on=config_dict['treada']['stages']['light_on'])
    )



