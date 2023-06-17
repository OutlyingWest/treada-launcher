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
            if line.startswith(var_name):
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
        # pd.set_option('display.float_format', '{:.8e}'.format)
        # print(df)
        # return df

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

    def prepare_dataframe(self):
        pass

    def save_prepared_file(self, prepared_file_path: str):
        pass


if __name__ == '__main__':
    op = TreadaOutputParser('C:\\Users\\px\\PycharmProjects\\treada-launcher\\data\\treada_raw_output.txt')
    print('rel time:', op.relative_time)
    print(op.dataframe)
