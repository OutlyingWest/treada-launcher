import os
import sys
from typing import List, Tuple, Union

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

from wrapper.config.config_builder import load_config


def main():
    config = load_config('config.json')
    result_path = os.path.split(config.paths.treada_result_output)[0] + os.sep
    if len(sys.argv) > 1:
        res_name = sys.argv[1]
    else:
        print('Enter file name to load data from data/result/. Example: "res_u(-0.45).txt"')
        res_name = input()
    full_result_path = result_path + res_name
    plot_builder(full_result_path)


def plot_builder(res_path: str,
                 plot_path: Union[str, None] = None,
                 skip_rows=11,
                 special_points: List[Tuple[float, float]] = None,
                 points_annotation: Union[str, None] = None):
    df = pd.read_csv(res_path, skiprows=skip_rows, header=0, sep='\s+')
    u_value = res_path.rsplit(os.sep, maxsplit=1)[1].split('(')[1].rsplit(')', maxsplit=1)[0]
    figure_title = 'Udrm = ' + u_value + ' V'
    plotter(df[df.columns[0]], df[df.columns[1]],
            x_label='time (ps)',
            y_label='I (mA/cm^2)',
            fig_title=figure_title,
            special_points=special_points,
            points_annotation=points_annotation)

    if plot_path:
        plt.savefig(plot_path)
    try:
        plt.show()
    except KeyboardInterrupt:
        pass


def plotter(x, y,
            x_label='x', y_label='y',
            fig_title='Transient',
            special_points: List[Tuple[float, float]] = None,
            points_annotation: Union[str, None] = None):
    fig, ax = plt.subplots(1, 1)
    # Set window title
    window = fig.canvas.manager.window
    window.title(fig_title)
    # Set plot title
    ax.set_title(fig_title)
    ax.grid(True)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # Set and display special points on plot if they exist
    if special_points:
        for point in special_points:
            special_x, special_y = point
            # Create special point
            plt.scatter(special_x, special_y, color='red', marker='o', s=30)
            # Annotate point
            if points_annotation:
                annotation = points_annotation
            else:
                annotation = f'({special_x}, {special_y})'

            plt.annotate(text=annotation,
                         xy=(special_x, special_y),
                         xytext=(10, -20),
                         textcoords='offset points',
                         arrowprops=dict(arrowstyle='->', color='black'))
    ax.plot(x, y)


if __name__ == '__main__':
    # Добавить путь к директории "wrapper" в переменную окружения PYTHONPATH
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "wrapper"))
    sys.path.append(wrapper_path)
    main()
