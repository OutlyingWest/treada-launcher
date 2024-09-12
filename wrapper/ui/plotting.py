import os
import re
import sys
from typing import Union, Iterable, Dict, Any, List

from colorama import Fore, Style

import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout, QPushButton
)


import pandas as pd

# Add path to "project" directory in environ variable - PYTHONPATH for cases of independent launch
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_path)

from wrapper.core.data_management import (
    TransientResultData, transient_cols, FileManager, TransientParameters, MtutManager, small_signal_cols
)
from wrapper.config.config_build import load_config, Config
from wrapper.misc import lin_alg as la
from wrapper.ui.console import ConsoleUserInteractor


def main():
    config = load_config('config.json')
    run_res_plotting(config)


def run_res_plotting(config: Config):
    app = QApplication()
    user_interactor = ConsoleUserInteractor()
    result_path = os.path.split(config.paths.result.main)[0] + os.sep
    print(f'{result_path=}')
    run_flag = True
    plot_builder = None
    full_mtut_path = os.path.join(project_path, config.paths.treada_core.mtut)
    while run_flag:
        print('Enter file name to load data from data/result/. Example: "res_u(-0.45).txt"')
        res_name = input()
        if res_name == '':
            app.quit()
            break

        full_result_path = os.path.join(project_path, result_path, res_name)
        print(f'{full_result_path=}')
        transient_cols.custom = config.advanced_settings.result.dataframe.custom['name']
        plot_builder = update_transient_plot(plot_builder, full_mtut_path, full_result_path, config.plotting.y_column)
        # Show plot
        plot_builder.plot_window.show()


class TransientPlotBuilder:
    """
    Download result data of treada-launcher from file and build plot.
    Can save plot picture to file.

    Attributes:
        result_path: path to result data file
        result_full_df: result data pandas dataframe
        plotter: TransientAdvancedPlotter class object

    Methods:
        set_descriptions(): sets plot descriptions
        set_transient_ending_point(coords: tuple, annotation: str): sets transient ending point
        _extract_udrm(res_path: str): extracts udrm value from result file path string
        show(): calls plt.show() method
        save_plot(plot_path: str): save plot to file
    """
    def __init__(self,
                 mtut_path: str,
                 result_path: str,
                 dist_path: Union[str, None] = None,
                 stage_name='none',
                 runtime_result_data: Union[Any, None] = None,
                 skip_rows=15,
                 x_transient_col_name=transient_cols.time,
                 y_transient_col_key='current_density',
                 is_transient_ending_point=False):
        self.dist_path = dist_path
        # Load result data from file
        self.result = self.load_result(mtut_path, result_path, skip_rows)
        # Extract result data
        self.y_transient_col_name = self.get_col_string_name_by_key(y_transient_col_key)
        x_column = self.result.full_df[x_transient_col_name]
        y_column = self.result.full_df[self.y_transient_col_name]
        # Create plotter object
        self.plotter = TransientAdvancedPlotter(x_column, y_column)
        self.legends = [self.plotter.ax.get_legend()]
        self.handles = [self.plotter.handle]
        res_name = self.extract_res_name(result_path)
        self.res_params = ResParams(name=res_name, last_time=x_column.iloc[-1])
        self.res_names_list = [res_name]
        # Create Qt plot window object
        self.plot_window = PlotWindow(self.plotter.fig, self.plotter.ax)
        # Construct plot
        self.set_descriptions(stage_name, y_label=self.y_transient_col_name)
        self.runtime_result_data = None
        self.is_transient_ending_point = is_transient_ending_point
        if runtime_result_data:
            self.runtime_result_data = runtime_result_data
            if self.is_transient_ending_point:
                ending_point_coords = (runtime_result_data.transient.corrected_time,
                                       runtime_result_data.transient.corrected_density)
                self.set_transient_ending_point(ending_point_coords, f'Transient ending point')

    def construct_plot_title(self):
        udrm = float(self.result.udrm)
        jpush = int(self.result.jpush)
        cklkrs = float(self.result.cklkrs)
        drstp = float(self.result.drstp)
        # If enabled point of drain (gate) potentials changing mode, show corresponding info, else show Udrm
        if jpush == 1 and cklkrs > 1:
            plot_title = f'Reaction for voltage step: Udrm = {udrm} → {udrm + drstp} V'
        else:
            plot_title = f'Напряжение на диоде = {udrm} B'
        return plot_title

    def set_descriptions(self, stage_name: str, x_label='time (ps)', y_label='I (mA/cm²)'):
        # Set titles
        plot_title = self.construct_plot_title()
        window_title = f'Udrm = {self.result.udrm} V stage: {stage_name}'
        self.plotter.set_plot_title(plot_title)
        self.plot_window.setWindowTitle(window_title)
        # Set axes labels
        self.plotter.set_plot_axes_labels(x_label=x_label, y_label=y_label)

    def change_descriptions(self, plot_title, window_title):
        # Set titles
        self.plotter.set_plot_title(plot_title)
        self.plot_window.setWindowTitle(window_title)

    def set_transient_ending_point(self, coords: tuple, annotation: str, xytext=(10, -20)):
        time, current_density = coords
        self.plotter.add_special_point(time, current_density)
        # self.plotter.annotate_special_point(time, current_density, annotation, xytext=xytext)

    def set_loaded_info(self):
        self.plotter.set_info(self.result)
        # Temporary results
        # Set distributions info if it exists
        if self.runtime_result_data and self.runtime_result_data.ww_data_indexes:
            try:
                ww_points_df = self.result.full_df.loc[self.runtime_result_data.ww_data_indexes]
                self.plotter.set_distributions_info(dist_times=ww_points_df[transient_cols.time],
                                                    dist_y=ww_points_df[self.y_transient_col_name])
            except KeyError as e:
                print(f'{Fore.YELLOW}Using "preserve_distributions": true option with '
                      f'"select_mean_dataframe": true option.\n'
                      f'Distributions preserving points can not be showed on plots due to an\n'
                      f'Exception: {e}\n'
                      f'Disable one of these options to avoid this warning.{Style.RESET_ALL}')

    def set_short_info(self, legend: str):
        self.legends.append(legend)
        self.plotter.legend(self.handles, self.legends)

    def set_advanced_info(self, y_col_name=transient_cols.current_density):
        self.plotter.set_advanced_info(self.runtime_result_data)
        # Set distributions info if it exists
        if self.runtime_result_data.ww_data_indexes:
            ww_points_df = self.result.full_df.loc[self.runtime_result_data.ww_data_indexes]
            self.plotter.set_distributions_info(dist_times=ww_points_df[transient_cols.time],
                                                dist_y=ww_points_df[y_col_name])

    @staticmethod
    def get_col_string_name_by_key(col_key):
        return transient_cols.__dict__[col_key]

    @staticmethod
    def _extract_udrm(res_path: str) -> Union[str, None]:
        udrm: re.Match = re.search('(-?\d+\.?\d*)', res_path)
        return udrm.group()

    @staticmethod
    def extract_stage_name(res_path: str) -> Union[str, None]:
        stage_name: re.Match = re.search('_(\w+).txt$', res_path)
        return stage_name.group(1)

    def extract_res_name(self, res_path: str) -> Union[str, None]:
        stage_name = self.extract_stage_name(res_path)
        res_name_with_path = re.sub(f'_{stage_name}.txt', '', res_path)
        res_name: re.Match = re.search('res_.*', res_name_with_path)
        return res_name.group()

    @staticmethod
    def load_result(mtut_path: str, result_path: str, skip_rows: int) -> TransientResultData:
        result_file_manager = FileManager(result_path)
        result_file_manager.load_file_head(num_lines=15)
        mtut_file_manager = MtutManager(mtut_path)
        mtut_file_manager.load_file()
        transient_time_str = result_file_manager.get_var('TRANSIENT_TIME')
        transient_time = float(transient_time_str.strip(' ps'))
        transient_density_str = result_file_manager.get_var('TRANSIENT_CURRENT_DENSITY')
        transient_density = float(transient_density_str.rstrip(' mA/cm^2'))
        transient_data = TransientParameters(
            corrected_time=transient_time,
            corrected_density=transient_density,
        )
        results = TransientResultData(
            transient=transient_data,
            udrm=result_file_manager.get_var('UDRM').strip(' V'),
            drstp=mtut_file_manager.get_var('DRSTP'),
            jpush=mtut_file_manager.get_var('JPUSH'),
            cklkrs=mtut_file_manager.get_var('CKLKRS'),
            emini=result_file_manager.get_var('EMINI'),
            emaxi=result_file_manager.get_var('EMAXI'),
            full_df=pd.read_csv(result_path, skiprows=skip_rows, header=0, sep='\s+'),
        )
        return results

    @staticmethod
    def find_duplicates(checked_list: list) -> dict:
        index_dict = {}
        for ind, item in enumerate(checked_list):
            if item in index_dict:
                index_dict[item].append(ind)
            else:
                index_dict[item] = [ind]
        duplicates = {item: indexes for item, indexes in index_dict.items() if len(indexes) > 1}
        return duplicates

    def correct_time_seria(self, actual_time_seria: pd.Series, res_path: str) -> pd.Series:
        res_name = self.extract_res_name(res_path)
        self.res_params.append(res_name, actual_time_seria.iloc[-1])
        print(f'{self.res_params=}')
        duplicated_names_dict = self.find_duplicates(self.res_params.names)
        print(f'{duplicated_names_dict=}')
        if duplicated_names_dict:
            _, dupl_indexes = duplicated_names_dict.popitem()
            first_dupl_index, last_dupl_index = dupl_indexes
            corrected_time_seria = actual_time_seria + self.res_params.last_times[first_dupl_index]
            self.res_params.last_times[last_dupl_index] = corrected_time_seria.iloc[-1]
            self.res_params.pop(first_dupl_index)
            print(f'After pop {self.res_params=}')
        else:
            corrected_time_seria = actual_time_seria
        return corrected_time_seria

    def add_plot(self, x, y, *args, **kwargs):
        handle, = self.plotter.add_plot(x, y, *args, **kwargs)
        self.handles.append(handle)

    @classmethod
    def save_plot(cls, plot_path: str):
        plt.savefig(plot_path)


class ResParams:
    def __init__(self, name: str, last_time: float):
        self.names = [name]
        self.last_times = [last_time]

    def append(self, name, last_time):
        self.names.append(name)
        self.last_times.append(last_time)

    def pop(self, index: int):
        self.names.pop(index)
        self.last_times.pop(index)

    def __repr__(self):
        return f'{self.__class__.__name__}(names={self.names},last_times={self.last_times})'


class SimplePlotter:
    """
    Allows to construct a single plot with labels and titles.

    Attributes:
        fig: Matplotlib Figure object
        ax: Matplotlib Axes object
    """
    def __init__(self, x: Iterable, y: Iterable, label='', plot_type='plot'):
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
            self.handle, = self.ax.plot(x, y, label=label)
        elif plot_type == 'scatter':
            self.handle, = self.ax.scatter(x, y, label=label)
        else:
            raise ValueError('Wrong type')

    def set_window_title(self, title='window title'):
        window = self.fig.canvas.manager.window
        # If Plotter was called by Qt - use QtAgg
        backend_name = matplotlib.get_backend()
        print(backend_name)
        if backend_name == 'QtAgg':
            window.setWindowTitle(title)
        elif backend_name == 'TkAgg':
            window.title(title)
        else:
            raise EnvironmentError('Wrong matplotlib backend. Use QtAgg or TkAgg')

    def set_plot_axes_labels(self, x_label='x', y_label='y'):
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

    def set_plot_title(self, title='plot title'):
        self.ax.set_title(title)

    def add_plot(self, x, y, *args, **kwargs):
        return self.ax.plot(x, y, *args, **kwargs)

    def legend(self, *args, **kwargs):
        self.ax.legend(*args, **kwargs)

    @classmethod
    def show(cls, block=True):
        try:
            plt.show(block=block)
        except KeyboardInterrupt:
            pass


class SpecialPointsMixin:
    """
    Allows to draw and annotate special points on plots.
    """
    @staticmethod
    def add_special_point(special_x, special_y, color='red', marker='o', size=30, zorder=5, **kwargs):
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
    def annotate_special_point(special_x, special_y, annotation='', xytext=(10, -20)):
        """
        Annotate special point.

        :param special_x: Special point x coordinate.
        :param special_y: Special point y coordinate.
        :param annotation: Point annotation.
        :param xytext: Annotation text coords.
        :return:
        """
        if not annotation:
            annotation = f'({special_x:.5f}, {special_y:.5f})'
        plt.annotate(text=annotation,
                     xy=(special_x, special_y),
                     xytext=xytext,
                     textcoords='offset points',
                     arrowprops=dict(arrowstyle='->', color='black'))


class PlotWindow(QWidget):
    def __init__(self, fig, ax, window_title=None):
        super().__init__()
        # self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 800, 600)  # Set window size
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # Create a custom toolbar with the "Graph Type" drop-down menu
        canvas = FigureCanvas(fig)
        custom_toolbar = MyCustomToolbar(canvas, self, fig, ax)
        layout.addWidget(canvas)
        layout.addWidget(custom_toolbar)


class MyCustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, fig, ax):
        super().__init__(canvas, parent)
        self.fig = fig
        self.ax = ax
    #     self.x_low_limit, self.x_high_limit = ax.get_xlim()
    #     self.y_low_limit, self.y_high_limit = ax.get_ylim()
    #
    #     limits_label = QLabel('Limits')
    #
    #     self.x_limits_widget = LimitsLineWidget(name='x:', limits=f'{self.x_low_limit:.3e}, {self.x_high_limit:.3e}')
    #     self.y_limits_widget = LimitsLineWidget(name='y:', limits=f'{self.y_low_limit:.3e}, {self.y_high_limit:.3e}')
    #     self.reset_button = QPushButton(text='Reset limits')
    #
    #     self.x_limits_widget.line_edit.textEdited.connect(self.update_x_limits)
    #     self.y_limits_widget.line_edit.textEdited.connect(self.update_y_limits)
    #     self.reset_button.clicked.connect(self.reset_limits)
    #
    #     self.addWidget(limits_label)
    #     self.addWidget(self.x_limits_widget)
    #     self.addWidget(self.y_limits_widget)
    #     self.addWidget(self.reset_button)
    #
    # def update_x_limits(self):
    #     x_limits = self.x_limits_widget.line_edit.text()
    #     try:
    #         low_limit, high_limit = re.split(r'\s*,\s*', x_limits)
    #         low_limit_number = float(low_limit)
    #         high_limit_number = float(high_limit)
    #     except ValueError:
    #         return
    #     self.ax.set_xlim(low_limit_number, high_limit_number)
    #     self.fig.canvas.draw()
    #
    # def update_y_limits(self):
    #     y_limits = self.y_limits_widget.line_edit.text()
    #     try:
    #         low_limit, high_limit = re.split(r'\s*,\s*', y_limits)
    #         low_limit_number = float(low_limit)
    #         high_limit_number = float(high_limit)
    #     except ValueError:
    #         return
    #     self.ax.set_ylim(low_limit_number, high_limit_number)
    #     self.fig.canvas.draw()

    # def reset_limits(self):
    #     # Reset plot canvas limits
    #     self.ax.set_xlim(self.x_low_limit, self.x_high_limit)
    #     self.ax.set_ylim(self.y_low_limit, self.y_high_limit)
    #     # Reset line edit text
    #     self.x_limits_widget.line_edit.setText(f'{self.x_low_limit:.3e}, {self.x_high_limit:.3e}')
    #     self.y_limits_widget.line_edit.setText(f'{self.y_low_limit:.3e}, {self.y_high_limit:.3e}')
    #     self.fig.canvas.draw()


class LimitsLineWidget(QWidget):
    def __init__(self, name: str, limits: str):
        super().__init__()
        label = QLabel(name)
        self.line_edit = QLineEdit(limits)

        layout = QHBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)


class TransientAdvancedPlotter(SpecialPointsMixin, SimplePlotter):
    """
    Class that extends the abilities of SimplePlotter.
    """
    def __init__(self, x: Iterable, y: Iterable, plot_type='plot'):
        super().__init__(x, y, plot_type=plot_type)

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

            ending_time_low = mean_df[transient_cols.time].loc[ending_index_low]
            ending_time_high = mean_df[transient_cols.time].loc[ending_index_high]

            ending_density_low = mean_df[transient_cols.current_density].loc[ending_index_low]
            ending_density_high = mean_df[transient_cols.current_density].loc[ending_index_high]

            # Plot rough transient ending point
            # self.add_special_point(results.transient.time, results.transient.current_density,
            #                        label='')  # Rough transient ending point
            # For report
            self.ax.scatter([], [], c='red', label='Оценка времени окончания переходного процесса')

            # Plot accurate transient ending point
            self.add_special_point(corrected_time, corrected_density, color='yellow', marker='*', size=70, zorder=4,
                                   label='Точное время окончания переходного процесса (τ)')
            self.ax.scatter([], [], label=f'τ = {results.transient.corrected_time:.2f} пс', s=0)

            # Plot transient ending condition line
            last_time = mean_df[transient_cols.time].iloc[-1]
            lines_length = last_time / 2
            nearest_ending_times, nearest_ending_densities = la.extend_line(x_coords=[results.transient.time,
                                                                                      ending_time_high],
                                                                            y_coords=[results.transient.current_density,
                                                                                      results.transient.current_density],
                                                                            line_length=lines_length)
            self.ax.plot(nearest_ending_times, nearest_ending_densities, c='red',
                         label='Уровень окончания переходного процесса',)
            # Plot mean current densities
            self.ax.scatter(mean_df[transient_cols.time],
                            mean_df[transient_cols.current_density],
                            c='green', alpha=1, zorder=2,
                            label='Усредненная плотность тока')
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

            self.ax.legend()
        else:
            raise ValueError('Results data does not set for plotting.')

    def set_distributions_info(self, dist_times: Iterable, dist_y: Iterable):
        self.ax.scatter(dist_times,
                        dist_y,
                        c='magenta', alpha=1, zorder=3,
                        label='WW measures points')
        self.ax.legend()


class WWDataPlotter(SimplePlotter):
    def __init__(self, ww_dict: dict, stage_name: str, plot_type='plot', backend='TkAgg'):
        # Set backend (Qt applications often require QtAgg backend)
        matplotlib.use(backend)
        last_ww_dir_key, last_ww_number_dict = ww_dict.popitem()
        ww_number, last_ww_df = last_ww_number_dict.popitem()
        super().__init__(x=last_ww_df['x'], y=last_ww_df[last_ww_df.columns[2]],
                         label=last_ww_dir_key, plot_type=plot_type)
        legends_list = self.add_bulk_plots(ww_dict, stage_name, is_describe_first=False)
        legends_list.append(last_ww_dir_key)
        legends_list[0] = f'{legends_list[0]} {stage_name} ww{ww_number}'
        self.legend(legends_list)

    def add_bulk_plots(self, ww_dict, stage_name: str, is_describe_first=True) -> list:
        old_legend = self.ax.get_legend()
        legends_list = list()
        ww = -1
        for ww_dir_key, ww_number_dict in ww_dict.items():
            ww_number, ww_df = next(iter(ww_number_dict.items()))
            self.add_plot(x=ww_df['x'], y=ww_df[ww_df.columns[2]])
            legends_list.append(ww_dir_key)
            ww = ww_number
        # Add descriptions to the first element of legend
        if is_describe_first:
            legends_list[0] = f'{legends_list[0]} {stage_name} ww{ww}'
        if old_legend:
            old_legends_list = [text.get_text() for text in old_legend.get_texts()]
            old_legends_list.extend(legends_list)
            return old_legends_list
        else:
            return legends_list



    @classmethod
    def interactive_mode_enable(cls):
        plt.ion()


class SmallSignalPlotter(SimplePlotter):
    """
    Class that extends the abilities of SimplePlotter.
    """
    def __init__(self, x: Iterable, y: Iterable, plot_type='plot'):
        super().__init__(x, y, '', plot_type)


class ImpedancePlotBuilder:
    """
    Download result data of treada-launcher from file and build plot.
    Can save plot picture to file.

    Attributes:

    Methods:

    """
    def __init__(self,
                 result_path: str,
                 skip_rows=None):
        self.result_df = self.load_result(result_path, skip_rows)
        self.freq_direction = ''
        # Create plotter objects
        self.plotters = self.create_plotters()
        self.set_descriptions()

    @staticmethod
    def load_result(result_path, skip_rows) -> pd.DataFrame:
        df = pd.read_csv(result_path, skiprows=skip_rows, header=0, sep='\s+')
        return df

    def create_plotters(self):
        z_parameter_real, z_parameter_img = self.calculate_z_parameter()
        self.freq_direction = self.define_frequency_direction(z_parameter_real)
        inverted_z_parameter_img = -z_parameter_img
        impedance_plotter = SmallSignalPlotter(x=z_parameter_real,
                                               y=inverted_z_parameter_img)

        frequency_hz = 1e9 * self.result_df[small_signal_cols.frequency]
        y_img_frequency_plotter = SmallSignalPlotter(x=frequency_hz,
                                                     y=self.result_df[small_signal_cols.y22.img])
        plotters = {
            'impedance': impedance_plotter,
            'y.img': y_img_frequency_plotter,
        }
        return plotters

    def calculate_z_parameter(self) -> tuple:
        y22_real = self.result_df[small_signal_cols.y22.real]
        y22_img = self.result_df[small_signal_cols.y22.img]
        z_real = y22_real / (y22_real**2 + y22_img**2)
        z_img = -y22_img / (y22_real**2 + y22_img**2)
        print(pd.DataFrame({'z_real': z_real, 'z_img': z_img, }))
        return z_real, z_img

    @staticmethod
    def define_frequency_direction(z_real: pd.Series) -> str:
        z_diff = z_real.iloc[-1] - z_real.iloc[0]
        if z_diff > 0:
            frequency_direction = '▶'
        elif z_diff < 0:
            frequency_direction = '◀'
        else:
            raise ValueError('Wrong Z parameter vector.')
        return frequency_direction

    def set_descriptions(self):
        self.set_impedance_descriptions()
        self.set_y_img_descriptions()

    def set_impedance_descriptions(self):
        # self.plotters['impedance'].set_window_title()
        self.plotters['impedance'].ax.scatter([], [], label=f'Freq. growth direction {self.freq_direction}', s=0)
        self.plotters['impedance'].ax.legend()
        self.plotters['impedance'].set_plot_title()
        self.plotters['impedance'].set_plot_axes_labels(x_label='Re(Z), Om', y_label='-Im(Z), Om')

    def set_y_img_descriptions(self):
        # self.plotters['y.img'].set_window_title()
        self.plotters['y.img'].set_plot_title()
        self.plotters['y.img'].set_plot_axes_labels(x_label='F, Hz', y_label='Im(Y), Om^-1')

    def show(self):
        plt.show(block=False)

    @classmethod
    def save_plot(cls, plot_path: str):
        plt.savefig(plot_path)


def plot_joint_stages_data(scenario,
                           joint_stages: list,
                           mtut_path: str,
                           y_transient_col_key: str,
                           result_paths: List[str]) -> PlotWindow:
    """
    Plot combined data from all stages listed by join_stages option in config.json.
    In case if join_stages = [] - empty list, skip combined data plotting.
    :param scenario:
    :param joint_stages:
    :param mtut_path:
    :param y_transient_col:
    :param result_paths:
    :return:
    """
    plot_builder = None
    for ind, stage in enumerate(scenario.stages.__dict__.keys()):
        stage_number = ind + 1
        if stage_number in joint_stages:
            plot_builder = update_transient_plot(plot_builder=plot_builder,
                                                 mtut_path=mtut_path,
                                                 result_path=result_paths[ind],
                                                 y_transient_col_key=y_transient_col_key)
    return plot_builder.plot_window


def update_transient_plot(plot_builder: Union[TransientPlotBuilder, None],
                          mtut_path: str,
                          result_path: str,
                          y_transient_col_key) -> TransientPlotBuilder:
    if plot_builder is None:
        try:
            # Creation of plot builder object
            plot_builder = TransientPlotBuilder(mtut_path=mtut_path,
                                                result_path=result_path,
                                                y_transient_col_key=y_transient_col_key)
        except FileNotFoundError:
            print('Wrong file path or name.')
        plot_builder.set_loaded_info()
        stage_name = plot_builder.extract_stage_name(result_path)
        plot_builder.legends = [f'Udrm={plot_builder.result.udrm}B {stage_name}']
    else:
        plot_builder.change_descriptions(plot_title='', window_title=f'Multiple res plot')
        result = plot_builder.load_result(mtut_path=mtut_path, result_path=result_path, skip_rows=15)
        # Correct time seria if it is from next stage of same result
        time_seria = plot_builder.correct_time_seria(result.full_df[transient_cols.time],
                                                     result_path)
        plot_builder.result = result
        y_transient_col_name = plot_builder.get_col_string_name_by_key(y_transient_col_key)
        plot_builder.add_plot(x=time_seria, y=result.full_df[y_transient_col_name])
        stage_name = plot_builder.extract_stage_name(result_path)
        plot_builder.set_short_info(f'Udrm={result.udrm}B {stage_name}')
        plot_builder.plotter.fig.canvas.draw()
    return plot_builder


if __name__ == '__main__':
    main()
