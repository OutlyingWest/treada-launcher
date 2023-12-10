import os
import sys
import unittest
from pathlib import Path

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

from wrapper.config.config_build import load_config
from wrapper.ui.plotting import ImpedancePlotBuilder


class ImpedancePlotBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        result_path = Path('./res_small_signal_info.txt').absolute().as_posix()
        print(f'{result_path=}')
        self.plot_builder = ImpedancePlotBuilder(result_path)

    @unittest.skip
    def test_dataframe(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(self.plot_builder.result_df)

    @unittest.skip
    def test_calculate_z_parameter(self):
        z_real, z_img = self.plot_builder.calculate_z_parameter()
        print(pd.DataFrame({'z_real': z_real, '-z_img': -z_img}))

    def test_show(self):
        self.plot_builder.show()
