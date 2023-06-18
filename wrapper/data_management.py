import re
import time
from pprint import pprint

import pandas as pd


class MtutStageConfiger:
    def __init__(self, mtut_path: str):
        self.mtut_manager = MtutManager(mtut_path)

    def light_off(self, light_off_setup: dict):
        for key, value in light_off_setup.items():
            self.mtut_manager.set_var(key, value)
        self.mtut_manager.save_file()

    def light_on(self, light_on_setup: dict):
        for key, value in light_on_setup.items():
            self.mtut_manager.set_var(key, value)
        self.mtut_manager.save_file()


class MtutManager:
    def __init__(self, mtut_file_path):
        self.path = mtut_file_path
        self.data: list = self.load_file()

    def load_file(self):
        with open(self.path, "r") as mtut_file:
            data = mtut_file.readlines()
        return data

    def save_file(self):
        with open(self.path, "w") as mtut_file:
            for line in self.data:
                mtut_file.write(line)

    def find_var_string(self, var_name: str):
        for num_line, line in enumerate(self.data):
            if line.startswith(var_name + ' '):
                return num_line
        return -1

    def get_var(self, var_name: str):
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            print(f'This variable: {var_name} does not exist in MTUT file.')
            raise ValueError
        var_line = self.data[var_index]
        var_value = self._get_var_value_from_string(var_line, var_name)
        return var_value

    def set_var(self, var_name: str, new_value: str):
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            print(f'This variable: {var_name} does not exist in MTUT file.')
            raise ValueError
        var_line = self.data[var_index]
        new_var_line = self._set_var_value_to_string(var_line, var_name, new_value)
        self.data[var_index] = new_var_line

    @staticmethod
    def _get_var_value_from_string(var_line: str, var_name: str):
        pattern = r"\s*({})\s*\n*".format(re.escape(var_name))
        return re.sub(pattern, "", var_line).rstrip('\n')

    @staticmethod
    def _set_var_value_to_string(var_line: str, var_name: str, new_value: str):
        pattern = r"\s*({})\s*".format(re.escape(var_name))
        old_value = re.sub(pattern, "", var_line).rstrip('\n')
        new_var_line = var_line.replace(old_value, new_value)
        return new_var_line


class TreadaOutputParser:
    def __init__(self, raw_output_path: str):
        self.raw_output_path = raw_output_path
        self.source_current_name = 'TSRS (mA)'
        rel_time, prepared_dataframe = self.prepare_data()
        self.relative_time: float = rel_time
        self.dataframe: pd.DataFrame = prepared_dataframe

    def prepare_data(self):
        # Load raw treada output file
        data_list = self.load_raw_file(self.raw_output_path)
        # Set relative time
        rel_time = self.set_relative_time(data_list)
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
        pure_data_lines = [line.split(' ', 1)[0] for line in data_list if self.keep_line_regex(line)]

        end_time = time.time()
        execution_time = end_time - start_time
        print(f'Time of file cleaning:{execution_time:.2f}s')

        # Creation of dataframe with current in numeric format
        pure_df = pd.DataFrame({self.source_current_name: pure_data_lines})
        pure_df[self.source_current_name] = pure_df[self.source_current_name].astype(float)

        return pure_df

    @staticmethod
    def set_relative_time(data_list: list):
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
                raise ValueError('Error: RELATIVE TIME is not found.')
        return relative_time

    @staticmethod
    def keep_line_regex(string: str):
        numeric_data_pattern = r"[-+]?\d+\.\d+[eE][-+]?\d+\s+\d+\."
        match = re.match(numeric_data_pattern, string)
        if match:
            return True
        else:
            return False

    def get_prepared_dataframe(self):
        return self.dataframe

    def get_relative_time(self):
        return self.relative_time


class ResultDataCollector:
    def __init__(self, mtut_file_path, treada_raw_output_path):
        self.mtut_manager = MtutManager(mtut_file_path)
        self.treada_parser = TreadaOutputParser(treada_raw_output_path)
        # Set dataframe col names
        self.source_current_name = self.treada_parser.source_current_name
        self.time_col_name = 'time(ns)'
        self.current_density_col_name = 'I(mA/cm^2)'
        self.dataframe = self.treada_parser.get_prepared_dataframe()
        # Result data
        self.transient_time = None
        self.result_dataframe = None
        # Get necessary MTUT variables

    def prepare_result_data(self):
        self.time_col_calculate()
        self.transient_time = self.find_transient_time()
        self.current_density_col_calculate()
        self.result_dataframe = self.dataframe[[self.time_col_name, self.current_density_col_name]]
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # print(result_dataframe)
        # print(transient_time)

    def get_transient_time(self):
        if self.transient_time:
            return self.transient_time
        else:
            raise ValueError('Does not calculated yet. Call prepare_result_data() firstly.')

    def get_result_dataframe(self):
        if isinstance(self.result_dataframe, pd.DataFrame):
            return self.result_dataframe
        else:
            raise ValueError('Does not calculated yet. Call prepare_result_data() firstly.')

    def time_col_calculate(self):
        # Get operating time step from MTUT file
        operating_time_step = float(self.mtut_manager.get_var('TSTEP'))
        # Get relative time from treada raw output file
        relative_time = self.treada_parser.get_relative_time()
        # Calculate timestep constant
        time_step_const = operating_time_step * relative_time
        self.dataframe[self.time_col_name] = self.dataframe.index.values * time_step_const

    def transient_criteria_calculate(self):
        # Get max and min current from col
        max_current = self.dataframe[self.source_current_name].max()
        min_current = self.dataframe[self.source_current_name].min()
        ending_difference = 0.01*(max_current - min_current)

        # Get last value in current col and calculate criteria of transient ending
        tr_criteria = dict()
        last_current_value = self.dataframe[self.source_current_name].iloc[-1]
        tr_criteria['plus'] = last_current_value + ending_difference
        tr_criteria['minus'] = last_current_value - ending_difference

        return tr_criteria

    def transient_criteria_apply(self, tr_criteria_dict):
        # Calculation of transient ending criteria
        self.dataframe['transient_criteria'] = 0
        self.dataframe.loc[
                (self.dataframe[self.source_current_name] < tr_criteria_dict['plus']) &
                (self.dataframe[self.source_current_name] > tr_criteria_dict['minus']),
                'transient_criteria'] = 1
        # Get index on which ending criteria satisfied
        transient_ending_index = self.dataframe['transient_criteria'][::-1].idxmin()

        return transient_ending_index

    def find_transient_time(self):
        tr_criteria_dict = self.transient_criteria_calculate()
        transient_ending_index = self.transient_criteria_apply(tr_criteria_dict)
        return self.dataframe[self.time_col_name].iloc[transient_ending_index]

    def current_density_col_calculate(self):
        # Get Device Width (microns)
        device_width = float(self.mtut_manager.get_var('WIDTH'))
        # Get HY
        hy = float(self.mtut_manager.get_var('HY').rstrip(')').split('(')[1])
        # Calculate density col
        self.dataframe[self.current_density_col_name] = (
            self.dataframe[self.source_current_name] / (2*hy * device_width * 1e-8)
        )

    def save_result_to_file(self, prepared_file_path: str):
        pass


class ResultBuilder:
    def __init__(self, mtut_file_path: str, treada_raw_output_path: str, result_path: str):
        self.result_configer = ResultDataCollector(mtut_file_path, treada_raw_output_path)
        self.result_path = self.file_name_build(result_path)
        self.result_configer.prepare_result_data()

    def file_name_build(self, result_path: str):
        udrm_value = self.result_configer.mtut_manager.get_var('UDRM')
        return f'{result_path.split(".")[0]}u({udrm_value}).txt'

    def save_data(self):
        header = self.header_build()
        self.header_print(header)
        self.header_dump_to_file(header)
        self.dump_dataframe_to_file()

    def header_build(self):
        udrm_value = self.result_configer.mtut_manager.get_var('UDRM')
        emini_value = self.result_configer.mtut_manager.get_var('EMINI')
        emaxi_value = self.result_configer.mtut_manager.get_var('EMAXI')
        transient_time_value = self.result_configer.get_transient_time()
        header: list = [
            'Diode biased at:',
            f'UDRM = {udrm_value} V',
            '',
            'Minimum Edge of Illumination Bandwidth:',
            f'EMINI = {emini_value} eV',
            '',
            'Maximum Edge of Illumination Bandwidth:',
            f'EMAXI = {emaxi_value} eV',
            '',
            'Transient time:',
            f'TRANSIENT_TIME = {transient_time_value} ps',
            '',
            '',
        ]
        header = [line + '\n' for line in header]
        return header

    @staticmethod
    def header_print(header: list):
        for line in header:
            print(line.rstrip())

    def header_dump_to_file(self, header: list):
        with open(self.result_path, 'w') as res_file:
            res_file.writelines(header)

    def dump_dataframe_to_file(self):
        result_dataframe: pd.DataFrame = self.result_configer.get_result_dataframe()
        with open(self.result_path, 'a') as res_file:
            res_file.write(result_dataframe.to_string(index=False))
        # result_dataframe.to_csv(self.result_path, sep='')


if __name__ == '__main__':
    # op = TreadaOutputParser('C:\\Users\\px\\PycharmProjects\\treada-launcher\\data\\treada_raw_output.txt')
    # print('rel time:', op.relative_time)
    # print(op.dataframe)

    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', None)
    # mtm = MtutManager('C:\\Users\\px\\PycharmProjects\\treada-launcher\\TreadaTx_C\\MTUT')
    # print(mtm.get_var('TSTEP'))


    rc = ResultDataCollector('C:\\Users\\px\\PycharmProjects\\treada-launcher\\TreadaTx_C\\MTUT',
                            'C:\\Users\\px\\PycharmProjects\\treada-launcher\\data\\treada_raw_output.txt')

    rc.prepare_result_data()

