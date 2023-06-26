import os
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import pandas as pd


def main():
    config = load_config('wrapper/config.json')
    print('Enter voltage from required file name to load data. Example: "u(-0.4)"')
    path_ending = input()
    result_path = config.paths.treada_result_output.rsplit('.', maxsplit=1)[0] + path_ending + '.txt'
    plot_builder(result_path)


def plot_builder(res_path: str):
    df = pd.read_csv(res_path, skiprows=11, header=0, sep='\s+')
    u_value = res_path.rsplit(os.sep, maxsplit=1)[1].split('(')[1].rsplit(')', maxsplit=1)[0]
    figure_title = 'Udrm = ' + u_value + ' V'
    plotter(df[df.columns[0]], df[df.columns[1]],
            x_label='time (ns)',
            y_label='I (mA/cm^2)',
            fig_title=figure_title)

    try:
        plt.show()
    except KeyboardInterrupt:
        pass


def plotter(x, y, x_label='x', y_label='y', fig_title='Transient'):
    fig, ax = plt.subplots(1, 1)
    # Set window title
    window = fig.canvas.manager.window
    window.title(fig_title)
    # Set plot title
    ax.set_title(fig_title)
    ax.grid(True)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.plot(x, y)


if __name__ == '__main__':
    from wrapper.config.config_builder import load_config
    main()
else:
    from wrapper.config.config_builder import load_config
