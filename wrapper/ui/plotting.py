import os
import re
import sys
from typing import Union, Iterable, Dict

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd


def main():
    config = load_config('config.json')
    result_path = os.path.split(config.paths.output.result)[0] + os.sep
    if len(sys.argv) > 1:
        res_name = sys.argv[1]
    else:
        print('Enter file name to load data from data/result/. Example: "res_u(-0.45).txt"')
        res_name = input()
    full_result_path = result_path + res_name
    # Creation of plot builder object
    plot_builder = TreadaPlotBuilder(result_path=full_result_path)
    # Show plot
    plot_builder.show()


class TreadaPlotBuilder:
    """
    Download result data of treada-launcher from file and build plot.
    Can save plot picture to file.

    Attributes:
        result_path: path to result data file
        result_df: result data pandas dataframe
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
                 ending_point_coords: Union[tuple, None] = None,
                 transient_time=-1.,
                 skip_rows=11):
        self.result_path = result_path
        # Load result data from file
        self.result_df = pd.read_csv(result_path, skiprows=skip_rows, header=0, sep='\s+')
        # Extract result data
        time_column = self.result_df[self.result_df.columns[0]]
        current_density_column = self.result_df[self.result_df.columns[1]]
        # Create plotter object
        self.plotter = AdvancedPlotter(time_column, current_density_column)
        # Construct plot
        self.set_descriptions()
        if ending_point_coords:
            self.set_transient_ending_point(ending_point_coords, f'Transient time = {transient_time:.3f} ps')

    def set_descriptions(self):
        # Set titles
        udrm: str = self._extract_udrm(self.result_path)
        title = f'Udrm = {udrm} V'
        self.plotter.set_plot_title(title)
        self.plotter.set_window_title(title)
        # Set axes labels
        self.plotter.set_plot_axes_labels(x_label='time (ps)', y_label='I (mA/cm^2)')

    def set_transient_ending_point(self, coords: tuple, annotation: str):
        time, current_density = coords
        self.plotter.add_special_point(time, current_density)
        self.plotter.annotate_special_point(time, current_density, annotation)

    @staticmethod
    def _extract_udrm(res_path: str) -> Union[str, None]:
        udrm: re.Match = re.search('(-?\d+\.?\d*)', res_path)
        return udrm.group()

    @classmethod
    def show(cls, block=True):
        try:
            plt.show(block=block)
        except KeyboardInterrupt:
            pass

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
    def add_special_point(special_x, special_y, color='red', marker='o', size=30):
        """
        Creates a special point on a plot.

        :param special_x: Special point x coordinate
        :param special_y: Special point y coordinate
        :param color: Point color
        :param marker: Point marker type
        :param size: Point size
        :return: Special point coordinates
        """
        plt.scatter(special_x, special_y, color=color, marker=marker, s=size)
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
            annotation = f'({special_x}, {special_y})'
        plt.annotate(text=annotation,
                     xy=(special_x, special_y),
                     xytext=(10, -20),
                     textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color='black'))

    @classmethod
    def add_multiple_points(cls, points: Dict[str, tuple]):
        """
        Add the multiple special points with annotations.

        :param points: example: {'first': (x_coord, y_coord), 'second': (x_coord, y_coord)}
        """
        for annotation, coords in points.items():
            x, y = coords
            cls.add_special_point(x, y)
            cls.annotate_special_point(x, y, annotation)


class AdvancedPlotter(SpecialPointsMixin, SimplePlotter):
    """
    Class that extends the abilities of SimplePlotter.
    """
    def __init__(self, x: Iterable, y: Iterable, plot_type='plot'):
        super().__init__(x, y, plot_type)


if __name__ == '__main__':
    # Add path to "wrapper" directory in environ variable - PYTHONPATH
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(wrapper_path)
    from config.config_builder import load_config
    main()
else:
    from wrapper.config.config_builder import load_config
