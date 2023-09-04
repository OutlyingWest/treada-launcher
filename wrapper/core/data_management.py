import shutil
import warnings
from dataclasses import dataclass, field
import os
import re
import time
from typing import Union, List, Tuple, Dict

from colorama import Fore, Style

import pandas as pd

try:
    from wrapper.config.config_builder import Paths, ResultPaths
    from wrapper.misc.global_functions import create_dir
    from wrapper.misc import lin_alg as alg
except ModuleNotFoundError:
    from config.config_builder import Paths, ResultPaths
    from misc.global_functions import create_dir
    from misc import lin_alg as alg


class MtutStageConfiger:
    def __init__(self, mtut_path: str):
        self.mtut_manager = MtutManager(mtut_path)

    def light_off(self, light_off_setup: dict):
        self.mtut_manager.load_file()
        for key, value in light_off_setup.items():
            if key != 'name':
                self.mtut_manager.set_var(key, str(value))
        self.mtut_manager.save_file()

    def light_on(self, light_on_setup: dict):
        self.mtut_manager.load_file()
        for key, value in light_on_setup.items():
            if key != 'name':
                self.mtut_manager.set_var(key, str(value))
        self.mtut_manager.save_file()


class FileManager:
    """
    This class provide the abilities to get or set variables in "configuration" file

    Attributes:
        path: Path to data file
        data: Extracted from file data (available only after file loading by load_file() method)

    Methods:
        load_file(): Load data from configuration file.
        save_file(): Save changes to configuration file.
        find_var_string(var_name: str): Returns number of line on which variable was found.
        get_var(var_name: str) Get variable by its name from configuration file.
        set_var(var_name: str, new_value: str) Set a new value for a variable in configuration file.

    """

    def __init__(self, file_path: str):
        """
         Initialize the FileManager object. Sets path and loads data from configuration file.

        :param file_path: Path to configuration file.
        """
        self.path = file_path
        self.data: Union[List[str], None] = None

    def load_file(self) -> list:
        """
        Load data from configuration file.

        :return: list which contains the data from configuration file.
        """
        with open(self.path, "r") as file:
            self.data = file.readlines()
        return self.data

    def load_file_head(self, num_lines) -> list:
        with open(self.path, "r") as file:
            file_head = [next(file) for x in range(num_lines)]
        self.data = file_head
        return self.data

    def save_file(self):
        """
        Save data to configuration file.
        """
        with open(self.path, "w") as file:
            for line in self.data:
                file.write(line)

    def find_var_string(self, var_name: str) -> int:
        """
        Returns number of line on which variable was found.

        :param var_name: Variable name in configuration file.
        :return: Number of line on which variable was found or -1 if it does not found.
        """
        for num_line, line in enumerate(self.data):
            if line.startswith(var_name + ' '):
                return num_line
        return -1

    def get_var(self, var_name: str) -> str:
        """
        Get variable by its name from configuration file.

        :param var_name: Variable name.
        :return: Variable value.
        """
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            print(f'This variable: {var_name} does not exist in configuration file.')
            raise ValueError
        var_line = self.data[var_index]
        var_value = self._get_var_value_from_string(var_line, var_name)
        return var_value

    def set_var(self, var_name: str, new_value: str):
        """
        Set a new value for a variable in configuration file.

        :param var_name:
        :param new_value:
        """
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            print(f'This variable: {var_name} does not exist in configuration file.')
            raise ValueError
        var_line = self.data[var_index]
        new_var_line = self._set_var_value_to_string(var_line, var_name, new_value)
        self.data[var_index] = new_var_line

    @staticmethod
    def _get_var_value_from_string(var_line: str, var_name: str) -> str:
        """
        Retrieves value of the variable from string.
        :param var_line: String that contains variable.
        :param var_name: Variable name.
        :return: Variable value in string format.
        """
        pattern = r"\s*({})\s*\n*".format(re.escape(var_name))
        return re.sub(pattern, "", var_line).strip('\n =')

    @staticmethod
    def _set_var_value_to_string(var_line: str, var_name: str, new_value: str) -> str:
        """
        Set a new value to a variable string.

        :param var_line: String that contains a variable.
        :param var_name: Variable name.
        :param new_value: New value to a variable in string format.
        :return: String that contains the variable with the new value.
        """
        pattern = r"\s*({})\s*".format(re.escape(var_name))
        old_value = re.sub(pattern, "", var_line).rstrip('\n')
        new_var_line = var_line.replace(old_value, new_value)
        return new_var_line


class MtutManager(FileManager):
    """
    This class provide the abilities to get or set variables in "MTUT" file

    Attributes:
        mtut_file_path: Path to data file
    """

    def __init__(self, mtut_file_path: str):
        super().__init__(mtut_file_path)

    def get_hx_var(self) -> List[Dict[str, float]]:
        """
        Get variable by its name from configuration file.
        :return: list of HX values dictionaries: {'steps_amount': float, 'step': float}
        """
        hx_name = 'HX'
        first_hx_index = self.find_var_string(hx_name)
        if first_hx_index == -1:
            print(f'This variable: {hx_name} does not exist in configuration file.')
            raise ValueError
        hx_values_list = list()
        for hx_index in range(first_hx_index, first_hx_index + 30):
            hx_line = self.data[hx_index]
            if hx_line.startswith('*'):
                break
            hx_values = re.split('[()]|\s+', hx_line)
            hx_values_list.append({'steps_amount': float(hx_values[1]), 'step': float(hx_values[2])})
            hx_index += 1
        return hx_values_list

    def get_list_var(self, var_name: str, values_type=None) -> list:
        """
        Get variable that consists of values separated by commas.
        :param var_name: MTUTM file variable name.
        :param values_type: the type to which values will be cast.
        :return: list of variable values
        """
        var_string = self.get_var(var_name)
        var_list = re.split('\s*,\s*', var_string)
        if values_type:
            cast_var_list = [values_type(value) for value in var_list]
            return cast_var_list
        else:
            return var_list


@dataclass(frozen=True)
class DataFrameColNames:
    time: str
    source_current: str
    current_density: str
    mean_density: str


col_names = DataFrameColNames(
    time='time(ps)',
    source_current='TSRS (mA)',
    current_density='I(mA/cm^2)',
    mean_density='mean_density',
)


class TreadaOutputParser:
    """
    Parse and clean "Treada's" output, which is dumped to treada_raw_output.txt file.
    Extract data. That includes:
        1) Source current vector and saving it to the dataframe
        2) RELATIVE TIME
    Attributes:

    Methods:
    """

    def __init__(self, raw_output_path: str):
        self.raw_output_path = raw_output_path
        rel_time, prepared_dataframe = self.prepare_data()
        self.relative_time: float = rel_time
        self.dataframe: pd.DataFrame = prepared_dataframe

    def prepare_data(self):
        # Load raw treada output file
        data_list = self.load_raw_file(self.raw_output_path)
        # Set relative time
        rel_time = self.find_relative_time(data_list)
        # Create prepared dataframe with source currents
        prepared_dataframe = self.clean_data(data_list)
        return rel_time, prepared_dataframe

    @staticmethod
    def load_raw_file(raw_file_path: str) -> list:
        with open(raw_file_path, 'r') as file:
            data = file.readlines()
        return data

    def clean_data(self, data_list: list):
        start_time = time.time()
        # Get pure source current list
        keep_line_regex_func = self.keep_currents_line_regex
        pure_data_lines = [line.split(' ', 1)[0] for line in data_list if keep_line_regex_func(line)]

        end_time = time.time()
        execution_time = end_time - start_time
        # print(f'Time of file cleaning:{execution_time:.2f}s')

        # Creation of dataframe with current in numeric format
        pure_df = pd.DataFrame({col_names.source_current: pure_data_lines})
        pure_df[col_names.source_current] = pure_df[col_names.source_current].astype(float)

        return pure_df

    @staticmethod
    def find_relative_time(data_list: list):
        relative_time = None
        relatives_found = False
        line_cnt = 0
        for line in data_list:
            if line.startswith('RELATIVE UNITES:'):
                relatives_found = True
            if relatives_found and line.startswith('TIME:'):
                relative_time = float((line.split(' ')[2]))
                break
            line_cnt += 1
            if line_cnt > 500:
                raise ValueError('Error: RELATIVE TIME not found. Maybe EN language not enabled in MTUT file')
        return relative_time

    @staticmethod
    def keep_currents_line_regex(string: str) -> bool:
        numeric_data_pattern = r"[-+]?\d+\.\d+[eE][-+]?\d+\s+\d+\."
        match = re.match(numeric_data_pattern, string)
        if match:
            return True
        else:
            return False

    @staticmethod
    def temporary_results_line_found(string: str) -> bool:
        substring_index = string.find('TIME STEPS WERE MADE WITH STEP LENGTH HT')
        if substring_index != -1:
            return True
        else:
            return False

    def get_prepared_dataframe(self):
        return self.dataframe

    def get_relative_time(self):
        return self.relative_time


class TransientData:
    """
    Class that contains data about transient process results.
    Provides the safe access to its own attributes.

    Attributes:
        ending_index_low: Low border's index of ending condition line and current density's line intersection.
        ending_index_high: High border's index of ending condition line and current density's line intersection.
        current_density: value of current density on which transient process ends.
        time: rough value of time on which transient process ends.
        corrected_time: accurate value of time density on which transient process ends. Additionally corrected.
    """

    def __init__(self, **kwargs):
        self._window_size_denominator: Union[int, None] = kwargs.get('window_size_denominator')
        self._window_size: Union[int, None] = kwargs.get('window_size')
        self.default_window_size = kwargs.get('default_window_size', 100)
        self.ending_index: Union[int, None] = kwargs.get('ending_index')
        self.ending_index_low: Union[int, None] = kwargs.get('ending_index_low')
        self.ending_index_high: Union[int, None] = kwargs.get('ending_index_high')
        self.current_density: Union[float, None] = kwargs.get('current_density')
        self.last_mean_current_density: Union[float, None] = kwargs.get('last_mean_current_density')
        self.time: Union[float, None] = kwargs.get('time')
        self.corrected_time: Union[float, None] = kwargs.get('corrected_time')
        self.corrected_density: Union[float, None] = kwargs.get('corrected_density')
        self.criteria_calculating_df_slice: Tuple[Union[int, None]] = kwargs.get('criteria_calculating_df_slice')

    def set_window_size(self, window_size):
        self._window_size = window_size

    def get_window_size(self):
        if self._window_size is None and self._window_size_denominator is None:
            print(f'{Fore.YELLOW} window_size and window_size_denominator are not defined, window_size'
                  f' will be set to default, {self.default_window_size=}{Style.RESET_ALL}')
            self._window_size = self.default_window_size
            print(f'{Fore.YELLOW}Push the Enter button if you want to continue anyway.{Style.RESET_ALL}')
            input()
        elif self._window_size is None:
            print(f'{Fore.YELLOW} window_size is not defined, window_size'
                  f' will be set to default, {self.default_window_size=}{Style.RESET_ALL}')
            self._window_size = self.default_window_size
            print(f'{Fore.YELLOW}Push the Enter button if you want to continue anyway.{Style.RESET_ALL}')
            input()
        elif self._window_size < 10:
            print(f'{Fore.YELLOW}Too little {self._window_size=},'
                  f' window size set to {self.default_window_size=}{Style.RESET_ALL}')
            self._window_size = self.default_window_size
            print(f'{Fore.YELLOW}Push the Enter button if you want to continue anyway.{Style.RESET_ALL}')
            input()
        return self._window_size

    def set_window_size_denominator(self, window_size_denominator):
        self._window_size_denominator = window_size_denominator

    def get_window_size_denominator(self):
        """
        Can be None, in this case window_size will not be redefined.
        """
        if self._window_size_denominator is not None:
            if self._window_size_denominator < 4:
                old_window_size_denominator = self._window_size_denominator
                self._window_size_denominator = 3
                print(f'{Fore.YELLOW}Too little window_size_denominator={old_window_size_denominator},'
                      f' set to {self._window_size_denominator=}{Style.RESET_ALL}')
                print(f'{Fore.YELLOW}Push the Enter button if you want to continue anyway.{Style.RESET_ALL}')
                input()
        return self._window_size_denominator

    def get_ending_index(self) -> int:
        """
        Returns index in result dataframe, which corresponds calculated transient time.
        :return:
        """
        if self.ending_index:
            return self.ending_index
        else:
            raise ValueError('ending_index does not calculated yet.')

    def get_ending_indexes(self) -> Tuple[int, int]:
        """
        Returns index in result dataframe, which corresponds calculated transient time.
        :return:
        """
        if self.ending_index_low and self.ending_index_high:
            return self.ending_index_low, self.ending_index_high
        else:
            print(f'{self.ending_index_low=} {self.ending_index_high=}')
            raise ValueError('ending_index_low and ending_index_high does not calculated yet.')

    def get_current_density(self) -> float:
        if self.current_density:
            return float(self.current_density)
        else:
            raise ValueError('current_density does not calculated yet.')

    def get_corrected_current_density(self) -> float:
        if self.corrected_density:
            return float(self.corrected_density)
        else:
            raise ValueError('corrected_density does not calculated yet.')

    def get_time(self):
        if self.time:
            return self.time
        else:
            raise ValueError('time does not calculated yet. Call prepare_result_data() firstly.')

    def get_corrected_time(self):
        if self.corrected_time:
            return self.corrected_time
        else:
            raise ValueError('corrected_time does not calculated yet. Call prepare_result_data() firstly.')

    def set_criteria_calculating_df_slice(self, slice_dict: Dict[str, Union[int, None]]):
        """
        Set tuple: (start, stop, step) of means_dataframe slice, that may be set to exclude anomaly values
        form transient criteria calculations.
        :param slice_dict: slice indexes dict, that may be red from config file.
        """
        self.criteria_calculating_df_slice = (slice_dict['start'], slice_dict['stop'], slice_dict['step'])

    def get_criteria_calculating_df_slice(self):
        """
        Returns tuple: (start, stop, step) of means_dataframe slice, that may be set to exclude anomaly values
        form transient criteria calculations.
        """
        return self.criteria_calculating_df_slice

    window_size = property(fset=set_window_size, fget=get_window_size)
    window_size_denominator = property(fset=set_window_size_denominator, fget=get_window_size_denominator)


class ResultDataCollector:
    def __init__(self, mtut_file_path, result_paths: ResultPaths):
        self.mtut_manager = MtutManager(mtut_file_path)
        self.mtut_manager.load_file()
        self.treada_parser = TreadaOutputParser(result_paths.temporary.raw)
        # Set dataframe col names
        self.dataframe = self.treada_parser.get_prepared_dataframe()
        # Create dataframe which contains mean current densities and its dependencies
        self.mean_dataframe = pd.DataFrame()
        # Result data
        self.transient = TransientData()
        self.result_dataframe = None
        # Additional result
        self.last_mean_time = None
        self.last_mean_current_density = None
        # Distributions
        self.dist_result_path = result_paths.temporary.distributions
        self.ww_data_indexes = []

    def prepare_result_data(self, stage_name: str):
        self.add_null_current_on_first_stage()
        self.time_col_calculate()
        self.current_density_col_calculate()
        self.transient.time = self.find_transient_time()
        self.result_dataframe = self.dataframe[[col_names.time, col_names.current_density]]
        self.transient.get_ending_index()
        self.correct_transient_time(window_size=self.transient.window_size)

        self.last_mean_time, self.last_mean_current_density = (
            self.mean_dataframe[[col_names.time, col_names.current_density]].tail(50).mean()
        )
        self.ww_data_indexes = self.set_distributions_indexes(stage_name)
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # print(result_dataframe)
        # print(transient_time)

    def add_null_current_on_first_stage(self):
        """
        Add an initial null source current value to current dataframe on first stage of Treada's work
        """
        stage_indication_var = float(self.mtut_manager.get_var('CKLKRS'))
        if stage_indication_var < 2:
            # Adding a 0 current value to string with index = -1
            self.dataframe.loc[-1] = 0
            # Shifting index
            self.dataframe.index = self.dataframe.index + 1
            # Sorting by index
            self.dataframe = self.dataframe.sort_index()

    def time_col_calculate(self):
        # Get initial time step from MTUT file
        initial_time_step = float(self.mtut_manager.get_var('TSTEPH'))
        # Number of Time Seps Before the Change Initial/Operating Time Step.
        initial_steps_number = int(self.mtut_manager.get_var('NMBPZ0'))
        # Get operating time step from MTUT file
        operating_time_step = float(self.mtut_manager.get_var('TSTEP'))
        # Get relative time from treada raw output file
        relative_time = self.treada_parser.get_relative_time()
        # Calculate timestep constants
        initial_time_step_const = initial_time_step * relative_time
        operating_time_step_const = operating_time_step * relative_time
        incremented_initial_steps_number = initial_steps_number + 1
        self.dataframe.loc[
            self.dataframe.index.values < incremented_initial_steps_number,
            col_names.time
        ] = self.dataframe.index.values[:incremented_initial_steps_number] * initial_time_step_const

        last_initial_time = self.dataframe[col_names.time].iloc[initial_steps_number]

        self.dataframe.loc[
            self.dataframe.index.values >= incremented_initial_steps_number,
            col_names.time
        ] = (
                (self.dataframe.index.values[incremented_initial_steps_number:] - initial_steps_number) *
                operating_time_step_const + last_initial_time
        )

        # pd.set_option('display.max_rows', None)
        # print(self.dataframe)
        # print(f'{last_initial_time=}')
        # print(f'{initial_time_step=}')
        # print(f'{operating_time_step=}')
        # print(f'{initial_time_step_const=}')
        # print(f'{operating_time_step_const=}')
        # print(f'{relative_time=}')
        input()

    def get_mean_current_density_seria(self, window_size_denominator: Union[None, int]) -> pd.Series:
        dataframe_length = self.dataframe.shape[0]
        # Set window_size if denominator exists or use its own window_size value if not
        if window_size_denominator is not None:
            self.transient.window_size = int(dataframe_length / window_size_denominator)
        # Calculating
        mean_densities = (
            self.dataframe[col_names.current_density]
            .rolling(window=self.transient.window_size, step=self.transient.window_size, center=True)
            .mean()
        )
        print(f'transient.window_size={self.transient.window_size}')
        return mean_densities

    def current_density_col_calculate(self):
        # Get Device Width (microns)
        device_width = float(self.mtut_manager.get_var('WIDTH'))
        # Get HY
        hy = float(self.mtut_manager.get_var('HY').rstrip(')').split('(')[1])
        # Calculate density col
        self.dataframe[col_names.current_density] = (
                self.dataframe[col_names.source_current] / (2 * hy * device_width * 1e-8)
        )

    def find_transient_time(self) -> float:
        """
        Fills mean_dataframe. Calculates and returns transient time.
        :return: transient time
        """
        window_size_denominator = self.transient.get_window_size_denominator()
        # Fill mean_dataframe
        self.mean_dataframe[col_names.current_density] = (
            self.get_mean_current_density_seria(window_size_denominator)
        )
        self.mean_dataframe[col_names.time] = (
            self.dataframe[col_names.time].iloc[self.mean_dataframe.index]
        )
        self.mean_dataframe.drop(self.mean_dataframe.index[-1], inplace=True)
        tr_criteria_dict = self.transient_criteria_calculate()
        self.transient_criteria_apply(tr_criteria_dict)
        # print(f'{self.transient.ending_index_low=}')
        # print(f'{self.transient.ending_index_high=}')
        return self.mean_dataframe[col_names.time].loc[self.transient.ending_index]

    def transient_criteria_calculate(self) -> dict:
        # Excluding of anomaly values if it necessary
        start, stop, step = self.transient.get_criteria_calculating_df_slice()
        dropped_mean_dataframe = self.mean_dataframe.iloc[start:stop:step]
        # Get max and min current from col
        max_density = dropped_mean_dataframe[col_names.current_density].max()
        min_density = dropped_mean_dataframe[col_names.current_density].min()
        ending_difference = 0.01 * (max_density - min_density)
        # Get last value in current col and calculate criteria of transient ending
        tr_criteria = dict()
        last_density_value = dropped_mean_dataframe[col_names.current_density].iloc[-1]
        tr_criteria['plus'] = last_density_value + ending_difference
        tr_criteria['minus'] = last_density_value - ending_difference
        # print(f'{last_density_value=}')
        # print(f"{tr_criteria['minus']=}")
        return tr_criteria

    def transient_criteria_apply(self, tr_criteria: dict):
        # Calculation of transient ending criteria
        # self.mean_dataframe['transient_criteria'] = 0
        self.mean_dataframe['compare_plus'] = 0
        self.mean_dataframe['compare_minus'] = 0
        self.mean_dataframe.loc[self.mean_dataframe[col_names.current_density] > tr_criteria['minus'],
                                'compare_minus'] = 1
        self.mean_dataframe.loc[self.mean_dataframe[col_names.current_density] < tr_criteria['plus'],
                                'compare_plus'] = 1

        # Get indexes on which ending criteria satisfied
        ending_minus_index = self.mean_dataframe['compare_minus'][::-1].idxmin()
        ending_plus_index = self.mean_dataframe['compare_plus'][::-1].idxmin()

        if ending_minus_index < ending_plus_index:
            self.transient.ending_index = ending_plus_index
            self.transient.current_density = tr_criteria['plus']

        elif ending_plus_index < ending_minus_index:
            self.transient.ending_index = ending_minus_index
            self.transient.current_density = tr_criteria['minus']
        else:
            raise ValueError('transient_ending_index does not found.')

        # print(f"{tr_criteria['minus']=}")
        # print(f"{self.transient.current_density=}")
        #
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # print(self.mean_dataframe)

    def correct_transient_time(self, window_size: int) -> tuple:
        """
        Precises ending transient time and current density.
        :return: accurate_time, accurate_density
        """
        # Get rough estimated transient density
        ending_density = self.transient.get_current_density()
        # Get transient ending border data
        ending_center_index = self.transient.get_ending_index()

        ending_next_time = (
            self.mean_dataframe[col_names.time].loc[ending_center_index + window_size]
        )
        ending_next_index = (
            self.mean_dataframe.loc[ending_next_time == self.mean_dataframe[col_names.time]].index.values[0]
        )

        self.transient.ending_index_low = ending_center_index
        self.transient.ending_index_high = ending_next_index

        # Get borders' times and densities
        ending_index_low, ending_index_high = self.transient.get_ending_indexes()
        ending_time_low, ending_density_low = (
            self.mean_dataframe[[col_names.time, col_names.current_density]].loc[ending_index_low]
        )
        ending_time_high, ending_density_high = (
            self.mean_dataframe[[col_names.time, col_names.current_density]].loc[ending_index_high]
        )

        # print(self.mean_dataframe)
        # print(f'{ending_time_low=} {ending_density_low=}')
        # print(f'{ending_time_high=} {ending_density_high=}')

        # Rough estimated density line coefficients
        k_rough, b_rough = alg.line_coefficients(first_point_coords=[ending_time_low, ending_density],
                                                 second_point_coords=[ending_time_high, ending_density])
        # Borders' line coefficients
        k_border, b_border = alg.line_coefficients(first_point_coords=[ending_time_low, ending_density_low],
                                                   second_point_coords=[ending_time_high, ending_density_high])
        # Find intersection
        self.transient.corrected_time, self.transient.corrected_density = (
            alg.lines_intersection([k_rough, b_rough], [k_border, b_border])
        )
        return self.transient.corrected_time, self.transient.corrected_density

    def get_result_dataframe(self):
        if isinstance(self.result_dataframe, pd.DataFrame):
            return self.result_dataframe
        else:
            raise ValueError('result_dataframe does not calculated yet. Call prepare_result_data() firstly.')

    def get_mean_dataframe(self):
        if isinstance(self.mean_dataframe, pd.DataFrame):
            return self.mean_dataframe
        else:
            raise ValueError('mean_dataframe does not calculated yet. Call prepare_result_data() firstly.')

    def set_distributions_indexes(self, stage_name: str):
        full_dist_result_path = os.path.join(self.dist_result_path, stage_name)
        ww_data_indexes_iter = map(int, os.listdir(full_dist_result_path))
        ww_data_indexes: list = sorted(ww_data_indexes_iter)
        actual_ww_data_indexes = [index for index in ww_data_indexes if index < self.dataframe.index[-1]]
        return actual_ww_data_indexes


@dataclass
class ResultData:
    transient: TransientData
    udrm: str
    emini: str
    emaxi: str
    full_df: pd.DataFrame
    mean_df: pd.DataFrame = field(default=None)
    ww_data_indexes: list = field(default=None)
    drstp: str = field(default=None)
    jpush: str = field(default=None)
    cklkrs: str = field(default=None)


class ResultBuilder:
    def __init__(self, result_collector: ResultDataCollector, result_paths: ResultPaths, stage='light'):
        self.result_collector = result_collector
        self.results = self._extract_results()
        self.result_path = self.file_name_build(result_paths.main, stage=stage)
        header = self._header_build()
        self.header_length = len(header)
        self.save_data(header)

    def _extract_results(self) -> ResultData:
        results = ResultData(
            transient=self.result_collector.transient,
            udrm=self.result_collector.mtut_manager.get_var('UDRM'),
            emini=self.result_collector.mtut_manager.get_var('EMINI'),
            emaxi=self.result_collector.mtut_manager.get_var('EMAXI'),
            full_df=self.result_collector.get_result_dataframe(),
            mean_df=self.result_collector.mean_dataframe,
            ww_data_indexes=self.result_collector.ww_data_indexes,
        )
        return results

    def file_name_build(self, result_path: str, stage: str, file_extension='txt'):
        return f'{result_path.split(".")[0]}u({self.results.udrm})_{stage}.{file_extension}'

    def save_data(self, header) -> int:
        # Create output dir if it does not exist
        create_dir(self.result_path)
        self._header_dump_to_file(header)
        self._dump_dataframe_to_file()
        return len(header)

    def _header_build(self):
        # with open(answer_with_path, mode='r', encoding='utf-8') as answr:
        #     answer_string = answr.read()
        # answer_string_with_format = answer_string.format(
        #     first_name=obj.from_user.first_name,
        #     format_cmd=hcode('/format'),
        #     error=hcode('Error:')
        # )

        header: list = [
            'Diode biased at:',
            f'UDRM = {self.results.udrm} V',
            '',
            'Minimum Edge of Illumination Bandwidth:',
            f'EMINI = {self.results.emini} eV',
            '',
            'Maximum Edge of Illumination Bandwidth:',
            f'EMAXI = {self.results.emaxi} eV',
            '',
            'Transient process:',
            f'TRANSIENT_TIME = {self.results.transient.corrected_time} ps',
            f'TRANSIENT_CURRENT_DENSITY = {self.results.transient.corrected_density} mA/cm^2',
            '',
            f'LAST_MEAN_TIME = {self.result_collector.last_mean_time} ps',
            f'LAST_MEAN_DENSITY = {self.result_collector.last_mean_current_density} mA/cm^2',
            '',
            '',
        ]
        header = [line + '\n' for line in header]
        return header

    @staticmethod
    def _header_print(header: list):
        for line in header:
            print(line.rstrip())

    def _header_dump_to_file(self, header: list):
        with open(self.result_path, 'w') as res_file:
            res_file.writelines(header)

    def _dump_dataframe_to_file(self):
        with open(self.result_path, 'a') as res_file:
            # Save dataframe without indexes to file
            res_file.write(self.results.full_df.to_string(index=False))


class UdrmVectorManager:
    """
    Manage UDRM vector file, which is used if UDRM_vector_mode set in UDRM_vector_mode config.json
    """

    def __init__(self, udrm_vector_file_path):
        self.file_path = udrm_vector_file_path
        self.max_index: Union[int, None] = None

    def load(self) -> List[float]:
        """
        Loads UDRM vector from file
        :return:
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as vector_file:
                udrm_list = vector_file.readlines()
            if not udrm_list:
                raise ValueError('UDRM vector is empty.')
            self.set_max_index(udrm_list)
            udrm_float_list = [float(udrm.replace(',', '.')) for udrm in udrm_list]
        else:
            print(f'UDRM vector file does not found in path: {self.file_path}')
            raise FileNotFoundError
        return udrm_float_list

    def set_max_index(self, udrm_list: list):
        self.max_index = len(udrm_list) - 1

    def get_max_index(self):
        if isinstance(self.max_index, int):
            return self.max_index
        elif self.max_index is None:
            raise ValueError('max_index has not calculated yet')


if __name__ == '__main__':
    pass
