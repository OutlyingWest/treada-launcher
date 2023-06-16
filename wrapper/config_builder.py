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


@dataclass
class Config:
    paths: Paths
    stages: Stages


def load_config(config_path: str = None):
    # project_path = os.path.dirname((os.path.abspath(__file__))).rsplit('\\/', maxsplit=1)[0]
    script_path = os.path.dirname((os.path.abspath(__file__)))
    project_path = os.path.split(script_path)[0] + '\\'
    full_config_path = project_path + config_path
    print(full_config_path)

    with open(full_config_path, "r") as config_file:
        config_dict = json.load(config_file)
    # load configuration from file
    return Config(
        paths=Paths(treada_exe=project_path + config_dict['treada']['paths']['to_exe']),
        stages=Stages(light_off=config_dict['treada']['stages']['light_off'],
                      light_on=config_dict['treada']['stages']['light_on'])
    )



