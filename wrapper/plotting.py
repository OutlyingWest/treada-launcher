import matplotlib.pyplot as plt
import pandas as pd

from config_builder import load_config


def main():
    config = load_config('wrapper/config.json')
    print('Enter voltage from required file name to load data. Example: "u(-0.4)"')
    path_ending = input()
    result_path = config.paths.treada_result_output.rsplit('.', maxsplit=1)[0] + path_ending + '.txt'
    plot_builder(result_path)


def plot_builder(res_path):
    df = pd.read_csv(res_path, skiprows=11, header=0, sep='\s+')
    plotter(df[df.columns[0]], df[df.columns[1]],
            x_label='time (ns)',
            y_label='I (mA/cm^2)')

    try:
        plt.show()
    except KeyboardInterrupt:
        pass


def plotter(x, y, x_label='x', y_label='y'):
    fig, ax = plt.subplots(1, 1)
    ax.grid(True)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.plot(x, y)


if __name__ == '__main__':
    main()
