"""
Contains features for load configuration
"""
import os
import json
from dataclasses import dataclass
from typing import Union

from dacite import from_dict


@dataclass
class StageNames:
    light_on: str
    light_off: str


@dataclass
class Stages:
    """
    Info about switching rules for "Treada" work stages.
    """
    light_off: dict
    light_on: dict
    names: StageNames


# Paths section
@dataclass
class TreadaCorePaths:
    """
    Paths to "Treada" exe and its own dependent files.
    """
    exe: str
    mtut: str


@dataclass
class InputPaths:
    """
    Paths to input data for treada_launcher program.
    """
    udrm: str
    state: str


@dataclass
class TemporaryResultFilePaths:
    """
    Paths to text result data of treada_launcher program.
    """
    raw: str
    distributions: str


@dataclass
class ResultPaths:
    """
    Paths to output of treada_launcher program.
    """
    main: str
    plots: str
    temporary: TemporaryResultFilePaths


@dataclass
class Paths:
    """
    Class that collects paths to all.
    """
    treada_core: TreadaCorePaths
    input: InputPaths
    result: ResultPaths
    scenarios: str


@dataclass
class Scenario:
    active_name: str


@dataclass
class Modes:
    """
    Keeps data about runtime modes of treada_launcher program.
    """
    udrm_vector_mode: bool


@dataclass
class PlottingFlags:
    """
    Keeps flags that set rules for plotting.
    """
    enable: bool
    advanced_info: bool


@dataclass
class Flags:
    """
    Class that collects all flags.
    """
    plotting: PlottingFlags
    auto_ending: bool
    dark_result_saving: bool


@dataclass
class TransientSettings:
    """
    """
    window_size: int
    window_size_denominator: Union[int, None]


@dataclass
class AdvancedSettings:
    """
    """
    transient: TransientSettings


@dataclass
class Config:
    """
    Class that collects all data from config.json.
    """
    stages: Stages
    scenario: Scenario
    modes: Modes
    flags: Flags
    advanced_settings: AdvancedSettings
    paths: Paths
    distribution_filenames: list


def load_config(config_name: str = None) -> Config:
    script_path = os.path.dirname((os.path.abspath(__file__)))
    project_path = script_path.rsplit(sep=os.path.sep, maxsplit=2)[0] + os.path.sep
    full_config_path = os.path.sep.join([script_path, config_name])

    with open(full_config_path, "r") as config_file:
        config_dict = json.load(config_file)
    # load configuration from file
    config = from_dict(data_class=Config, data=config_dict)
    return config
