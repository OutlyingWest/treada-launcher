import os
import timeit
import unittest
from typing import Dict, List

import numpy as np

import matplotlib
import pandas as pd

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from wrapper.core.data_management import UdrmVectorManager, FileManager, TransientOutputParser, TransientResultDataCollector, \
    transient_cols, MtutManager, MtutDataFrameManager, SmallSignalInfoOutputParser
from wrapper.config.config_build import load_config
from wrapper.ui.plotting import TransientAdvancedPlotter


@unittest.skip
class UdrmVectorManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.udrm_vector = UdrmVectorManager(self.config.paths.input.udrm)
        print('UdrmVectorManagerTests')

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
class MtutManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.mtut = MtutManager(self.config.paths.treada_core.mtut)
        self.mtut.load_file()

    @unittest.skip
    def test_get_hx_var(self):
        hx = self.mtut.get_hx_var()
        print(f'{hx=}')
        self.assertEqual(type(hx), list)

    def test_get_list_var(self):
        var_name = 'CMOB2IL'
        var_list = self.mtut.get_list_var(var_name, values_type=float)
        print(f'{var_list}')
        self.assertEqual(type(var_list[0]), float)


class TreadaOutputParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.mtut = FileManager(self.config.paths.treada_core.mtut)
        self.mtut.load_file()
        self.transient_parser = TransientOutputParser(self.config.paths.result.temporary.raw)

    @unittest.skip
    def test_transient_clean_data_speed(self):
        data_list = TransientOutputParser.load_raw_file(self.config.paths.result.temporary.raw)
        clean_data_time = timeit.timeit(lambda: self.transient_parser.clean_data(data_list), number=1000)
        print(f'{clean_data_time=}')

    def test_small_signal_clean_data(self):
        small_signal_parser = SmallSignalInfoOutputParser(self.config.paths.result.temporary.raw)
        print(small_signal_parser.header_data)


@unittest.skip
class ResultDataCollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.rdc = TransientResultDataCollector(self.config.paths.treada_core.mtut, self.config.paths.result.temporary.raw)
        self.rdc.prepare_result_data()
        # self._df = self.rdc.get_result_dataframe()

    # @unittest.skip
    def test_ending_lines_intersection_algorythm(self):
        # Get data
        # self.rdc.time_col_calculate()
        # self.rdc.current_density_col_calculate()
        # self.rdc.transient_time = ending_time = self.rdc.find_transient_time()
        # ending_index_low, ending_index_high = self.rdc.transient.get_ending_indexes()
        # ending_current_density = self.rdc.transient.get_current_density()
        # # density_mean_seria = self.rdc.get_mean_current_density_seria()
        # # density_mean_times: pd.Series = self.rdc.dataframe[self.rdc.time_col_name].iloc[density_mean_seria.index]
        # self.rdc.mean_dataframe[self.rdc.time_col_name] = (
        #     self.rdc.dataframe[self.rdc.time_col_name].iloc[self.rdc.mean_dataframe.index]
        # )
        # self.transient_current_density = self.rdc.result_dataframe[self.rdc.current_density_col_name].iloc[ending_index_high]
        # accurate_time, accurate_density = self.rdc.correct_transient_time()
        ending_time = self.rdc.transient.get_time()
        ending_current_density = self.rdc.transient.get_current_density()
        ending_index_low, ending_index_high = self.rdc.transient.get_ending_indexes()
        accurate_time = self.rdc.transient.get_corrected_time()
        accurate_density = self.rdc.transient.get_corrected_current_density()

        print(f'{accurate_time=}')
        print(f'{accurate_density=}')


        # desities = pd.DataFrame()

        print(f'{ending_current_density=}')
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # print(self.rdc.mean_dataframe)

        print(f'{ending_index_low=}')
        print(self.rdc.mean_dataframe.loc[ending_index_low])
        print(f'{ending_index_high=}')
        print(self.rdc.mean_dataframe.loc[ending_index_high])
        print(self.rdc.mean_dataframe.loc[ending_index_low-1000:ending_index_low+1000])
        # print(type(density_mean_times))

        # init plotter
        self.plotter = TransientAdvancedPlotter(self.rdc.dataframe['time(ns)'], self.rdc.dataframe['I(mA/cm^2)'])
        # Plot rough transient ending point
        self.plotter.add_special_point(ending_time, ending_current_density,
                                       label='Rough transient ending point')
        # Plot mean current densities
        self.plotter.ax.scatter(self.rdc.mean_dataframe[transient_cols.time],
                                self.rdc.mean_dataframe[transient_cols.current_density],
                                c='green', alpha=1, zorder=2,
                                label='Mean current densities')
        # Highlight low nearest ending point
        self.plotter.ax.scatter(self.rdc.mean_dataframe[transient_cols.time].loc[ending_index_low],
                                self.rdc.mean_dataframe[transient_cols.current_density].loc[ending_index_low],
                                c='black', alpha=1, zorder=3,
                                label='Low nearest ending point')
        # Highlight high nearest ending point
        self.plotter.ax.scatter(self.rdc.mean_dataframe[transient_cols.time].loc[ending_index_high],
                                self.rdc.mean_dataframe[transient_cols.current_density].loc[ending_index_high],
                                c='magenta', alpha=1, zorder=3,
                                label='High nearest ending point')
        # Plot accurate transient ending point
        self.plotter.add_special_point(accurate_time, accurate_density, color='yellow', marker='*', size=70, zorder=4,
                                       label='Accurate transient ending point')
        self.plotter.annotate_special_point(accurate_time, accurate_density)
        self.plotter.ax.legend()

        plt.show()
        # plt.scatter

    @unittest.skip
    def test_means_dataframe(self):
        # init plotter
        self.plotter = TransientAdvancedPlotter(self.rdc.dataframe['time(ns)'], self.rdc.dataframe['I(mA/cm^2)'])
        # Plot mean current densities
        self.plotter.ax.scatter(self.rdc.mean_dataframe[self.rdc.time_col_name],
                                self.rdc.mean_dataframe[self.rdc.current_density_col_name],
                                c='green', alpha=1, zorder=2,
                                label='Mean current densities')
        plt.show()


@unittest.skip
class InputDataFrameManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.manager = MtutDataFrameManager(self.config.paths.input.mtut_dataframe)

    def test_load_input_df(self):
        df = self.manager.get()
        print(df)
        print(df['CMOB2IL'])
        vars_seria: pd.Series = df.iloc[0]
        for var_key, var_value in vars_seria.items():
            print(f'{var_key=} {var_value=}')
            print(f'{type(var_key)=}')



if __name__ == '__main__':
    unittest.main()
