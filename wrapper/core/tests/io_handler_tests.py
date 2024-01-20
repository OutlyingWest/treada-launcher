import os
import unittest
import numpy as np
import pandas as pd

from wrapper.core.treada_io_handling import EndingCondition
from wrapper.ui.plotting import plot_builder
from wrapper.config.config_build import load_config


class EndingConditionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ending_condition = EndingCondition(chunk_size=100,
                                                equal_values_to_stop=5,
                                                deviation_coef=1e-5)
        self.config = load_config('config.json')

    def test_is_equal(self):
        arr = np.array([50, 21, 33, -10, 20])
        equal = self.ending_condition.is_satisfied(arr, deviation=61)
        self.assertEqual(equal, True)

        arr = np.array([50, 21, 33, -10, 20])
        equal = self.ending_condition.is_satisfied(arr, deviation=30)
        self.assertEqual(equal, False)

    def test_check(self):
        result_path = os.path.split(self.config.paths.treada_result_output)[0] + '\\res_u(-1.49).txt'
        print(f'{result_path = }')
        df = pd.read_csv(result_path, skiprows=11, header=0, sep='\s+')

        true_conditions = list()
        print(df.index)
        for time, current in zip(df.index, df[df.columns[1]]):
            if self.ending_condition.check(current):
                true_conditions.append((time, current))
        # print(true_conditions)

        plot_builder(result_path, special_points=true_conditions)

        # arr = np.array([50, 21, 33, -10, 20])
        # equal = self.ending_condition.is_equal(arr, deviation=61)
        # self.assertEqual(equal, True)


if __name__ == '__main__':
    unittest.main()
