"""
Contains features for load configuration
"""
import os
import json
from dataclasses import dataclass
from typing import Union, Dict

from dacite import from_dict, Config

from wrapper.misc.global_functions import get_from_nested_dataclass, set_to_nested_dataclass


@dataclass
class Scenario:
    active_name: str


@dataclass
class Modes:
    """
    Keeps data about runtime modes of treada_launcher program.
    """
    udrm_vector_mode: bool
    mtut_dataframe: bool


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
    preserve_distributions: bool
    fields_calculation: bool


@dataclass
class LightImpulse:
    """
    """
    consider_fixed_time: bool
    fixed_time_ps: float


@dataclass
class DarkImpulse:
    """
    """
    for_stages: list
    consider_fixed_time: bool
    fixed_time_ps: float


@dataclass
class EndingCondition:
    """
    Simple ending condition settings.
    """
    chunk_size: int
    equal_values_to_stop: int
    deviation: float


@dataclass
class RuntimeSettings:
    """
    """
    find_relative_time: bool
    light_impulse: LightImpulse
    dark_impulse: DarkImpulse
    ending_condition: EndingCondition


@dataclass
class TransientSettings:
    """
    """
    window_size: int
    window_size_denominator: Union[int, None]
    criteria_calculating_df_slice: dict


@dataclass
class CommonDataFrameCols:
    """
    """
    time: bool
    current_density: bool


@dataclass
class DataFrameCols(CommonDataFrameCols):
    source_current: bool


@dataclass
class MeanDataFrameCols(CommonDataFrameCols):
    pass


@dataclass
class ResultSettings:
    """
    """
    select_mean_dataframe: bool
    dataframe: DataFrameCols
    mean_dataframe: MeanDataFrameCols


@dataclass
class AdvancedSettings:
    """
    """
    runtime: RuntimeSettings
    transient: TransientSettings
    result: ResultSettings

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
    mtut_dataframe: str
    states: str


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
    resources: str


@dataclass
class Config:
    """
    Class that collects all data from config.json.
    """
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
    # Construct absolute paths
    paths_dict = get_from_nested_dataclass(config.paths)
    for key, path in paths_dict.items():
        paths_dict[key] = os.path.join(project_path, path)
    set_to_nested_dataclass(config.paths, paths_dict)
    return config
