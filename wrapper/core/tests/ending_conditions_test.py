import os
import unittest
import time

import numpy as np

import matplotlib
import pandas as pd

from wrapper.ui.plotting import AdvancedPlotter

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from wrapper.core.data_management import UdrmVectorManager, FileManager, TreadaOutputParser
from wrapper.config.config_builder import load_config
from wrapper.core.ending_conditions import StepBasedEndingCondition, LineEndingCondition, MeansEndingCondition


# @unittest.skip('skip line tests')
# class LineEndingConditionTests(unittest.TestCase):
#     def setUp(self) -> None:
#         self.config = load_config('config.json')
#         # self.lec = LineEndingCondition(precision=0.001,
#         #                                     chunk_size=3,
#         #                                     big_step_multiplier=1,
#         #                                     low_step_border=5)
#
#         self.lec = LineEndingCondition(precision=1e-2,
#                                        chunk_size=100,
#                                        big_step_multiplier=100,
#                                        low_step_border=100)
#
#         # Initials:
#
#         # -- Generated --
#         # start_x = 0
#         # stop_x = 600
#         # self.X = np.arange(start_x, stop_x, 1)
#         # self.Y = -600 / np.exp(self.X/60) + 600
#
#         # -- Real --
#         result_path = os.path.split(self.config.paths.output.result)[0] + os.sep + 'res_u(-16.0).txt'
#         # Load result data from file
#         self.result_full_df = pd.read_csv(result_path, skiprows=11, header=0, sep='\s+')
#         # Extract result data
#         self.X = list(self.result_full_df.index)
#         self.Y = self.result_full_df[self.result_full_df.columns[1]]
#         print(f'{self.Y}')
#
#         self.plotter = AdvancedPlotter(self.X, self.Y, plot_type='plot')
#
#     def test_check(self):
#         condition_list = []
#         for x, y in zip(self.X, self.Y):
#             # for chunks in self.lec.ping_pong:
#             #     if chunks[0].__class__.__name__ == 'ChunkSmall':
#             #         self.plotter.add_special_point(chunks[0].x, chunks[0].y, color='green')
#             #     elif chunks[0].__class__.__name__ == 'ChunkBig':
#             #         self.plotter.add_special_point(chunks[0].x, chunks[0].y, color='red')
#             #     if False and x > 550 and hasattr(chunks[0], 'k'):
#             #         k = chunks[0].k
#             #         self.plotter.annotate_special_point(chunks[0].x, chunks[0].y, annotation=f'{k=}')
#
#             # print(f'{x, y}')
#             # print(f'{self.lec.ping_pong=}')
#             # print(self.lec.ping_pong)
#
#             condition = self.lec.check(current_index=x, source_current=y)
#
#             if x == self.X[-1]:
#                 for chunks in self.lec.ping_pong:
#                     for chunk in chunks:
#                         print(chunk.x, chunk.y)
#                         if chunk.__class__.__name__ == 'ChunkSmall':
#                             self.plotter.add_special_point(chunk.x, chunk.y, color='green')
#                         elif chunk.__class__.__name__ == 'ChunkBig':
#                             self.plotter.add_special_point(chunk.x, chunk.y, color='red')
#                         if hasattr(chunk, 'k'):
#                             k = chunk.k
#                             self.plotter.annotate_special_point(chunk.x, chunk.y, annotation=f'Last {k=}')
#             # condition_list.append(condition)
#             if condition:
#                 for chunks in self.lec.ping_pong:
#                     for chunk in chunks:
#                         print(chunk.x, chunk.y)
#                         if chunk.__class__.__name__ == 'ChunkSmall':
#                             self.plotter.add_special_point(chunk.x, chunk.y, color='green')
#                         elif chunk.__class__.__name__ == 'ChunkBig':
#                             self.plotter.add_special_point(chunk.x, chunk.y, color='red')
#                         if hasattr(chunk, 'k'):
#                             k = chunk.k
#                             self.plotter.annotate_special_point(chunk.x, chunk.y, annotation=f'{k=}')
#                 break
#         # self.result_full_df['condition'] = condition_list
#
#         # pd.set_option('display.max_rows', None)
#         # print(self.result_full_df.loc[self.result_full_df['condition'] == True].index)
#         plt.show()
#
#     def test_speed_check(self):
#         start_time = time.time()
#         for x, y in zip(self.X, self.Y):
#             self.lec.check(current_index=x, source_current=y)
#         end_time = time.time()
#         execution_time = end_time - start_time
#         print(f'Execution time:{execution_time:.4f}s')


class MeansEndingConditionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')

        self.mec = MeansEndingCondition(precision=2e-5,
                                        chunk_size=100,
                                        big_step_multiplier=100,
                                        low_step_border=100)

        # Initials:

        # -- Generated --
        # start_x = 0
        # stop_x = 600
        # self.X = np.arange(start_x, stop_x, 1)
        # self.Y = -600 / np.exp(self.X/60) + 600

        # -- Real --
        result_path = os.path.split(self.config.paths.output.result)[0] + os.sep + 'res_u(-7.0).txt'
        # Load result data from file
        self.result_df = pd.read_csv(result_path, skiprows=11, header=0, sep='\s+')
        # Extract result data
        self.X = list(self.result_df.index)
        self.Y = self.result_df[self.result_df.columns[1]]
        print(f'{self.Y}')

        self.plotter = AdvancedPlotter(self.X, self.Y, plot_type='plot')

    def test_check(self):
        condition_list = []
        for x, y in zip(self.X, self.Y):
            condition = self.mec.check(current_index=x, source_current=y)

            # if x == self.X[-1]:
            #     for chunks in self.mec.ping_pong:
            #         for chunk in chunks:
            #             print(chunk.x, chunk.y)
            #             if chunk.__class__.__name__ == 'ChunkSmall':
            #                 self.plotter.add_special_point(chunk.x, chunk.y, color='green')
            #             elif chunk.__class__.__name__ == 'ChunkBig':
            #                 self.plotter.add_special_point(chunk.x, chunk.y, color='red')
            #             self.plotter.annotate_special_point(chunk.x, chunk.y, annotation=f'Last points')
            # condition_list.append(condition)
            if condition:
                for chunks in self.mec.ping_pong:
                    for chunk in chunks:
                        if chunk.__class__.__name__ == 'ChunkSmall':
                            self.plotter.add_special_point(chunk.x, chunk.y, color='green')
                        elif chunk.__class__.__name__ == 'ChunkBig':
                            self.plotter.add_special_point(chunk.x, chunk.y, color='red')
            if condition or x == self.X[-1]:
                print(f'{self.mec.ping_pong[1][0].x=}')
                print(f'{self.mec.ping_pong[1][1].x=}')
                print(f'{self.mec.ping_pong[1][0].y - self.mec.ping_pong[1][1].y=}')

                print(f'{self.mec.current_scale}*{self.mec.precision} = {self.mec.current_scale * self.mec.precision}')
                print(f'{self.mec.max_current=} {self.mec.min_current=}')
                print(f'{self.mec.ping_pong[0][0].step=}')
                print(f'{self.mec.ping_pong[1][0].step=}')
                break

        # self.result_full_df['condition'] = condition_list

        # pd.set_option('display.max_rows', None)
        # print(self.result_full_df.loc[self.result_full_df['condition'] == True].index)
        plt.show()

