import timeit
import unittest

import numpy as np

import matplotlib
import pandas as pd

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from wrapper.core.data_management import UdrmVectorManager, FileManager, TreadaOutputParser, ResultDataCollector
from wrapper.config.config_builder import load_config
from wrapper.ui.plotting import AdvancedPlotter


@unittest.skip
class UdrmVectorManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.udrm_vector = UdrmVectorManager(self.config.paths.input.udrm)

    def test_load(self):
        if self.config.modes.udrm_vector_mode:
            try:
                udrm_vector = self.udrm_vector.load()
            except Exception:
                self.fail()
            self.assertTrue(udrm_vector, 'UDRM vector do not loaded from file or not exists')


@unittest.skip
class FileManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.mtut = FileManager(self.config.paths.treada_core.mtut)
        self.mtut.load_file()

    def test__get_var_value_from_string(self):
        var_value = self.mtut._get_var_value_from_string(var_line='RIMPUR   3.E+12', var_name='RIMPUR')
        self.assertEqual('3.E+12', var_value)


@unittest.skip
class TreadaOutputParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.mtut = FileManager(self.config.paths.treada_core.mtut)
        self.mtut.load_file()
        self.parser = TreadaOutputParser(self.config.paths.output.raw)

    # def test_prepare_data_speed(self):
    #     prepare_data_time = timeit.repeat('parser.prepare_data()',
    #                                       setup=f"from wrapper.core.data_management import TreadaOutputParser;"
    #                                             f"parser = TreadaOutputParser(fr'{self.config.paths.output.raw}');",
    #                                       repeat=10,
    #                                       number=50)
    #     print(f'{np.mean(prepare_data_time)=}')
    #
    # def test_load_raw_file_speed(self):
    #     load_raw_file_time = timeit.repeat('parser.load_raw_file(raw_output_path)',
    #                                       setup=f"from wrapper.core.data_management import TreadaOutputParser;"
    #                                             f"parser = TreadaOutputParser(fr'{self.config.paths.output.raw}');"
    #                                             f"raw_output_path = parser.raw_output_path"
    #                                             f"",
    #                                       repeat=10,
    #                                       number=50)
    #     print(f'{np.mean(load_raw_file_time)=}')

    def test_clean_data_speed(self):
        clean_data_time = timeit.repeat('prepared_dataframe = parser.clean_data(data_list)',
                                          setup=f"from wrapper.core.data_management import TreadaOutputParser;"
                                                f"parser = TreadaOutputParser(fr'{self.config.paths.output.raw}');"
                                                f"raw_output_path = parser.raw_output_path;"
                                                f"data_list = parser.load_raw_file(raw_output_path);"
                                                f"",
                                          repeat=10,
                                          number=50)
        print(f'{np.mean(clean_data_time)=}')
        with open('clean_data_speeds.txt', 'a') as cd_file:
            cd_file.write(str(np.mean(clean_data_time)) + '\n')


class ResultDataCollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.rdc = ResultDataCollector(self.config.paths.treada_core.mtut, self.config.paths.output.raw)
        self.rdc.prepare_result_data()
        self.df = self.rdc.get_result_dataframe()

    def test_ending_lines_intersection(self):
        # Get data
        self.rdc.time_col_calculate()
        self.rdc.transient_time = self.rdc.find_transient_time()
        self.rdc.current_density_col_calculate()
        ending_index = self.rdc.get_transient_ending_index()
        ending_time = self.rdc.get_transient_time()
        ending_current_density = self.rdc.get_transient_current_density()
        print(f'{ending_index=}')
        print(f'{ending_current_density=}')
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        print(self.rdc.dataframe.iloc[74647-10: 74647+10])




        # init plotter
        self.plotter = AdvancedPlotter(self.rdc.dataframe['time(ns)'], self.rdc.dataframe['I(mA/cm^2)'])
        self.plotter.add_special_point(ending_time, ending_current_density)
        plt.show()





if __name__ == '__main__':
    unittest.main()
