import os
import sys
import unittest

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

from wrapper.config.config_build import load_config
from wrapper.ui.plotting import SimplePlotter


class SimplePlotterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simple_plotter = SimplePlotter()
        self.simple_plotter.init_plot([1,2], [1,2])
