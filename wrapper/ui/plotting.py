import os
import re
import sys
from typing import Union, Iterable, Dict, Any, List

import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd


def main():
    try:
        from config.config_builder import load_config

        config = load_config('config.json')
        result_path = os.path.split(config.paths.result.main)[0] + os.sep
        print(f'{result_path=}')
    except ModuleNotFoundError:
        print('Finding of input file by full path...')
        result_path = ''
    run_flag = True
    while run_flag:
        if len(sys.argv) > 1:
            res_name = sys.argv[1]
        else:
            print('Enter file name to load data from data/result/. Example: "res_u(-0.45).txt"')
            res_name = input()
            if res_name == '':
                break

        full_result_path = result_path + res_name
        try:
            # Creation of plot builder object
            plot_builder = TreadaPlotBuilder(result_path=full_result_path)
        except FileNotFoundError:
            print('Wrong file path or name.')
            continue
        plot_builder.set_loaded_info()
        # Show plot
        plot_builder.plotter.show(block=False)


class TreadaPlotBuilder:
    """
    Download result data of treada-launcher from file and build plot.
    Can save plot picture to file.

    Attributes:
        result_path: path to result data file
        result_full_df: result data pandas dataframe
        plotter: AdvancedPlotter class object

    Methods:
        set_descriptions(): sets plot descriptions
        set_transient_ending_point(coords: tuple, annotation: str): sets transient ending point
        _extract_udrm(res_path: str): extracts udrm value from result file path string
        show(): calls plt.show() method
        save_plot(plot_path: str): save plot to file
    """
    def __init__(self,
                 result_path: str,
                 stage='light',
                 result_data: Union[Any, None] = None,
                 ending_point_coords: Union[tuple, None] = None,
                 transient_time=-1.,
                 skip_rows=15):
        self.result_path = result_path
        # Load result data from file
        self.result_full_df = pd.read_csv(result_path, skiprows=skip_rows, header=0, sep='\s+')
        # Extract result data
        time_column = self.result_full_df[self.result_full_df.columns[0]]
        current_density_column = self.result_full_df[self.result_full_df.columns[1]]
        # Create plotter object
        self.plotter = AdvancedPlotter(time_column, current_density_column)
        # Construct plot
        self.set_descriptions(stage)
        if result_data:
            self.result_data = result_data
            ending_point_coords = (result_data.transient.corrected_time, result_data.transient.corrected_density)
            self.set_transient_ending_point(ending_point_coords, f'Transient ending point')

    def set_descriptions(self, stage_name: str):
        # Set titles
        udrm: str = self._extract_udrm(self.result_path)
        plot_title = f'Udrm = {udrm} V'
        window_title = f'{plot_title} stage: {stage_name}'
        self.plotter.set_plot_title(plot_title)
        self.plotter.set_window_title(window_title)
        # Set axes labels
        self.plotter.set_plot_axes_labels(x_label='time (ps)', y_label='I (mA/cm^2)')

    def set_transient_ending_point(self, coords: tuple, annotation: str):
        time, current_density = coords
        self.plotter.add_special_point(time, current_density)
        self.plotter.annotate_special_point(time, current_density, annotation)

    def set_loaded_info(self):
        loaded_result = self.load_result()
        self.plotter.set_info(loaded_result)

    def set_advanced_info(self):
        self.plotter.set_advanced_info(self.result_data)

    @staticmethod
    def _extract_udrm(res_path: str) -> Union[str, None]:
        udrm: re.Match = re.search('(-?\d+\.?\d*)', res_path)
        return udrm.group()

    def load_result(self) -> Any:
        file_manager = FileManager(self.result_path)
        file_manager.load_file_head(num_lines=11)
        transient_time_str = file_manager.get_var('TRANSIENT_TIME')
        transient_time = float(transient_time_str.strip(' ps'))
        transient_data = TransientData(
            corrected_time=transient_time
        )
        results = ResultData(
            transient=transient_data,
            udrm=file_manager.get_var('UDRM'),
            emini=file_manager.get_var('EMINI'),
            emaxi=file_manager.get_var('EMAXI'),
            full_df=None,
            mean_df=None,
        )
        return results

    @classmethod
    def save_plot(cls, plot_path: str):
        plt.savefig(plot_path)


class SimplePlotter:
    """
    Allows to construct a single plot with labels and titles.

    Attributes:
        fig: Matplotlib Figure object
        ax: Matplotlib Axes object
    """
    def __init__(self, x: Iterable, y: Iterable, plot_type='plot'):
        """
        Take coords to plot.
        :param x: Iterable vector of x coordinates
        :param y: Iterable vector of y coordinates
        """
        fig, ax = plt.subplots(1, 1)
        self.fig: plt.Figure = fig
        self.ax: plt.Axes = ax
        self.ax.grid(True)
        if plot_type == 'plot':
            self.ax.plot(x, y)
        elif plot_type == 'scatter':
            self.ax.scatter(x, y)
        else:
            raise ValueError('Wrong type')

    def set_window_title(self, title='window title'):
        window = self.fig.canvas.manager.window
        window.title(title)

    def set_plot_axes_labels(self, x_label='x', y_label='y'):
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

    def set_plot_title(self, title='plot title'):
        self.ax.set_title(title)


class SpecialPointsMixin:
    """
    Allows to draw and annotate special points on plots.
    """
    @staticmethod
    def add_special_point(special_x, special_y, color='red', marker='o', size=30, zorder=2, **kwargs):
        """
        Creates a special point on a plot.

        :param special_x: Special point x coordinate
        :param special_y: Special point y coordinate
        :param color: Point color
        :param marker: Point marker type
        :param size: Point size
        :param zorder: Order of sowing by z axis
        :return: Special point coordinates
        """
        plt.scatter(special_x, special_y, c=color, marker=marker, s=size, zorder=zorder, **kwargs)
        return special_x, special_y

    @staticmethod
    def annotate_special_point(special_x, special_y, annotation=''):
        """
        Annotate special point.

        :param special_x: Special point x coordinate.
        :param special_y: Special point y coordinate.
        :param annotation: Point annotation.
        :return:
        """
        if not annotation:
            annotation = f'({special_x:.5f}, {special_y:.5f})'
        plt.annotate(text=annotation,
                     xy=(special_x, special_y),
                     xytext=(10, -20),
                     textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color='black'))


class AdvancedPlotter(SpecialPointsMixin, SimplePlotter):
    """
    Class that extends the abilities of SimplePlotter.
    """
    def __init__(self, x: Iterable, y: Iterable, plot_type='plot'):
        super().__init__(x, y, plot_type)

    def set_info(self, loaded_result):
        self.ax.scatter([], [], label=f'EMINI = {loaded_result.emini}', s=0)
        self.ax.scatter([], [], label=f'EMAXI = {loaded_result.emaxi}', s=0)
        self.ax.scatter([], [], label=f'Transient time = {loaded_result.transient.corrected_time:.4f} ps', s=0)
        self.ax.legend()

    def set_advanced_info(self, results):
        if results:
            # Extract data
            ending_index_low = results.transient.ending_index_low
            ending_index_high = results.transient.ending_index_high
            corrected_time = results.transient.corrected_time
            corrected_density = results.transient.corrected_density
            mean_df = results.mean_df

            ending_time_low = mean_df[col_names.time].loc[ending_index_low]
            ending_time_high = mean_df[col_names.time].loc[ending_index_high]

            ending_density_low = mean_df[col_names.current_density].loc[ending_index_low]
            ending_density_high = mean_df[col_names.current_density].loc[ending_index_high]

            # Plot rough transient ending point
            # self.add_special_point(results.transient.time, results.transient.current_density,
            #                        label='')  # Rough transient ending point
            # For report
            self.ax.scatter([], [], c='red', label='Rough transient ending point')

            # Plot transient ending condition line
            last_time = mean_df[col_names.time].iloc[-1]
            lines_length = last_time / 2
            nearest_ending_times, nearest_ending_densities = la.extend_line(x_coords=[results.transient.time,
                                                                                      ending_time_high],
                                                                            y_coords=[results.transient.current_density,
                                                                                      results.transient.current_density],
                                                                            line_length=lines_length)
            self.ax.plot(nearest_ending_times, nearest_ending_densities, c='red',
                         label='Ending condition line',)
            # Plot mean current densities
            self.ax.scatter(mean_df[col_names.time],
                            mean_df[col_names.current_density],
                            c='green', alpha=1, zorder=2,
                            label='Mean current densities')
            # Highlight low nearest ending point
            self.ax.scatter(ending_time_low,
                            ending_density_low,
                            c='black', alpha=1, zorder=3,
                            label='')  # Low nearest ending point
            # Highlight high nearest ending point
            self.ax.scatter(ending_time_high,
                            ending_density_high,
                            c='magenta', alpha=1, zorder=3,
                            label='')  # High nearest ending point
            # Plot nearest means line
            nearest_ending_times, nearest_ending_densities = la.extend_line(x_coords=[ending_time_low,
                                                                                      ending_time_high],
                                                                            y_coords=[ending_density_low,
                                                                                      ending_density_high],
                                                                            line_length=lines_length)
            self.ax.plot(nearest_ending_times, nearest_ending_densities, c='black')
            # Plot accurate transient ending point
            self.add_special_point(corrected_time, corrected_density, color='yellow', marker='*', size=70, zorder=4,
                                   label='Accurate transient ending point')
            self.ax.scatter([], [], label=f'Transient time = {results.transient.corrected_time:.6f} ps', s=0)

            self.ax.legend()
        else:
            raise ValueError('Results data does not set for plotting.')

    @classmethod
    def show(cls, block=True):
        try:
            plt.show(block=block)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    # Add path to "wrapper" directory in environ variable - PYTHONPATH
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(wrapper_path)
    from core.data_management import ResultData, col_names, FileManager, TransientData
    from config.config_builder import load_config
    main()
else:
    from wrapper.core.data_management import ResultData, col_names, FileManager, TransientData
    from wrapper.config.config_builder import load_config
    from wrapper.misc import lin_alg as la
