"""
Contains features for load settings
"""
import os
from dataclasses import dataclass
from environs import Env


@dataclass()
class Paths:
    treada_exe_path: str


@dataclass
class Config:
    paths: Paths


def load_config(path: str = None):
    env = Env()
    env.read_env(path)
    project_path = os.path.dirname((os.path.abspath(__file__)))
    # load configuration from file
    return Config(
        paths=Paths(treada_exe_path=project_path + env.str('TREADA_EXE_PATH'))
    )
