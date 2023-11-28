import os
import re
import sys
import time
import weakref
from time import sleep
from typing import Dict, Union, List
import subprocess

import pandas as pd
from PySide6.QtCore import QObject, Slot, Signal, QThread
from PySide6.QtWidgets import QApplication


# Add path to "project" directory in environ variable - PYTHONPATH
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.sep.join([".."] * 4)))
sys.path.append(project_path)

from wrapper.config.config_builder import load_config, Config
from wrapper.ui.plotting import WWDataPlotter
from wrapper.misc.collections.ww_data_collecting.ui.main_window import MainWindow


def main():
    config = load_config('config.json')
    run_ww_collecting(config)


def run_ww_collecting(config: Config):
    ww_descriptions_path = os.path.join(config.paths.resources, 'ww_descriptions.csv')
    ww_data_collector = WWDataCollector(ww_descriptions_path, config.paths.result.temporary.distributions)
    if len(sys.argv) < 3:
        user_interactor = WWDataCmdUserInteractor(ww_data_collector)
    elif '--gui' in sys.argv:
        user_interactor = WWDataInterfaceUserInteractor(ww_data_collector)
    else:
        print('Wrong distr. collection command line argument.')
        return -1
    user_interactor.run()


class WWDataCollector:
    def __init__(self, descriptions_path: str, distributions_path: str):
        self.descriptions = self.load_descriptions(descriptions_path)
        self.distributions_path = distributions_path

    @staticmethod
    def load_descriptions(descriptions_path: str) -> pd.DataFrame:
        df = pd.read_csv(descriptions_path, header=0, sep='\s\s\s+', encoding='windows-1251', engine='python',
                         usecols=['description', 'df_col_name'], dtype={'df_col_name': str})
        # df.replace(to_replace='NaN', value=None, inplace=True)
        df.index += 1
        return df

    @staticmethod
    def extract_ww_data(data_folder_path: str):
        script_path = os.path.dirname((os.path.abspath(__file__)))

        cwd_paths = [os.path.join(data_folder_path, index_path) for index_path in os.listdir(data_folder_path)]
        exe_path = os.path.join(script_path, 'SplViewLQ.exe')

        for working_directory_path in cwd_paths:
            try:
                subprocess.run(exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=working_directory_path)
            except FileNotFoundError:
                print('Executable file not found, Path:', exe_path)

    @staticmethod
    def _construct_ww_folder_path(stage_dir_name: str, ww_dir_index: int, ww_file_ind: int) -> str:
        ww_file_name = f'WW{ww_file_ind}.DAT'
        relative_ww_data_path = os.path.join(stage_dir_name, str(ww_dir_index), ww_file_name)
        return relative_ww_data_path

    @classmethod
    def load_ww_data(cls, abs_res_path: str, stage_dir_name: str, ww_dir_indexes: list, ww_aliases: Dict[int, str]) -> dict:
        ww_data_dict = {}
        for ww_dir_index in ww_dir_indexes:
            ww_dir_index = int(ww_dir_index)
            ww_data_dict[ww_dir_index] = {}
            for ww_file_ind, ww_name in ww_aliases.items():
                relative_ww_data_path = cls._construct_ww_folder_path(stage_dir_name, ww_dir_index, ww_file_ind)
                full_ww_path = os.path.join(abs_res_path, relative_ww_data_path)
                # Index in extracted from data_folder paths list
                ww_dataframe = pd.read_csv(full_ww_path, sep='\s+')
                ww_dataframe.columns = ['x', 'y', ww_name]
                # Discard tail
                ww_dataframe = ww_dataframe.loc[ww_dataframe['y'] == 0.]
                ww_data_dict[ww_dir_index][ww_file_ind] = ww_dataframe
        return ww_data_dict

    @staticmethod
    def is_ww_data_exists(stage_folder_path: str):
        index_path = next(iter(os.listdir(stage_folder_path)))
        ww_path = os.path.join(stage_folder_path, index_path)
        file_names = os.listdir(ww_path)
        for file_name in file_names:
            if file_name.startswith('WW'):
                return True
        return False

    def extract_stages_ww_data(self, distributions_path: str, ignore_existence=False):
        for stage_folder_path in os.listdir(distributions_path):
            stage_folder_path = os.path.join(distributions_path, stage_folder_path)
            if ignore_existence:
                self.extract_ww_data(stage_folder_path)
            else:
                if not self.is_ww_data_exists(stage_folder_path):
                    self.extract_ww_data(stage_folder_path)

    def list_stage_dir_indexes(self, stage_name: str) -> list:
        stage_folder_path = os.path.join(self.distributions_path, stage_name)
        stage_data_index_strings: list = sorted(os.listdir(stage_folder_path), key=int)
        stage_data_indexes = [int(index_string) for index_string in stage_data_index_strings]
        return stage_data_indexes


class WWDataUserInteractor:
    # ww_data_plotter object can be created outside the __init__() function.
    __slots__ = ['__dict__', 'ww_data_plotter']

    def __init__(self, ww_data_collector: WWDataCollector):
        self.data_collector = ww_data_collector
        self.is_add_to_exists = False
        self.is_log_scale = False

    def _input_stage_name(self, stage_name=''):
        if stage_name in os.listdir(self.data_collector.distributions_path):
            return stage_name
        else:
            return None

    def _input_ww_folder_path(self, stage_name=''):
        stage_name = self._input_stage_name()
        if stage_name:
            ww_folder_path = os.path.join(self.data_collector.distributions_path, stage_name)
            return ww_folder_path
        else:
            return None

    def plot(self, stage_name: str,
             ww_dir_numbers_list: list,
             ww_number: int,
             df_col_name: str,
             backend='TkAgg') -> dict:
        ww_dict = self.data_collector.load_ww_data(abs_res_path=self.data_collector.distributions_path,
                                                   stage_dir_name=stage_name,
                                                   ww_dir_indexes=ww_dir_numbers_list,
                                                   ww_aliases={ww_number: df_col_name})

        ww_description = self.data_collector.descriptions['description'].loc[ww_number]
        if self.is_add_to_exists:
            self.is_add_to_exists = False
            if hasattr(self, 'ww_data_plotter'):
                self.ww_data_plotter.interactive_mode_enable()
                legends_list = self.ww_data_plotter.add_bulk_plots(ww_dict, stage_name)
                self.ww_data_plotter.legend(legends_list)
            else:
                print('Plot object not exists. Adding unavailable.')
        else:
            self.ww_data_plotter = WWDataPlotter(ww_dict, stage_name, backend=backend)
            self.ww_data_plotter.set_plot_axes_labels(x_label='x', y_label=ww_description)
            if df_col_name:
                self.ww_data_plotter.set_plot_title(df_col_name)
                self.ww_data_plotter.set_window_title(df_col_name)
            if self.is_log_scale:
                self.is_log_scale = False
                self.ww_data_plotter.ax.set_yscale('log', base=10)
            self.ww_data_plotter.show(block=False)
        return ww_dict

    def run(self):
        """
        Method to run user interactor application in cmd or interface mode.
        """
        pass


class WWDataCmdUserInteractor(WWDataUserInteractor):
    # ww_data_plotter object can be created outside the __init__() function.
    __slots__ = ['ww_data_plotter']

    def __init__(self, ww_data_collector: WWDataCollector):
        super().__init__(ww_data_collector)

    def run(self):
        running_flag = True
        while running_flag:
            self._greetings()
            try:
                user_input = input()
                cmd_code = 1
                while cmd_code:
                    cmd_code = self._check_command(user_input)
                    if cmd_code != 0:
                        self._greetings()
                        user_input = input()
                if cmd_code >= 0:
                    ww_number = self._convert_ww_number_to_show(user_input)
                    if ww_number:
                        df_col_name = self.data_collector.descriptions['df_col_name'].loc[ww_number]
                        stage_name = self._input_stage_name()
                    else:
                        stage_name = df_col_name = None
                    if stage_name:
                        all_ww_dir_numbers_list = self.data_collector.list_stage_dir_indexes(stage_name)
                        ww_dir_numbers_range = self._input_ww_dir_numbers_range(all_ww_dir_numbers_list)
                    else:
                        ww_dir_numbers_range = all_ww_dir_numbers_list = None
                    if ww_dir_numbers_range:
                        ww_dir_numbers_list = self._ww_range_to_list(ww_dir_numbers_range, all_ww_dir_numbers_list)
                        ww_dict = self.plot(stage_name=stage_name,
                                            ww_dir_numbers_list=ww_dir_numbers_list,
                                            ww_number=ww_number,
                                            df_col_name=df_col_name)
                        self.print_ww_dict(ww_dict)
            except KeyboardInterrupt:
                break
            self._footer()

    @staticmethod
    def _greetings():
        print('Введите номер WW-файла для отображения или команду.')
        print('Чтобы получить справку по всем командам, введите --help')
        print('Доступные номера WW-файлов и их описания можно посмотреть с помощью команды --ww')

    @staticmethod
    def _footer():
        print('Для полного выхода из программы нажмите: "Ctrl+C".', end='\n\n')

    def _convert_ww_number_to_show(self, ww_number_str: str) -> Union[int, None]:
        if ww_number_str.isnumeric():
            ww_number = int(ww_number_str)
            if ww_number in self.data_collector.descriptions.index:
                return ww_number
            else:
                print('Wrong WW number. Not in available range.')
                return None

    def _input_stage_name(self, stage_name=''):
        print("Введите имя директории в distributions/, соответствующей этапу работы Tread'ы:")
        stage_name = input()
        correct_stage_name = super(WWDataCmdUserInteractor, self)._input_stage_name(stage_name)
        if correct_stage_name:
            return correct_stage_name
        else:
            print('Wrong WW dir name')
            return None

    def _input_ww_dir_numbers_range(self, stage_dir_indexes: list) -> Union[list, None]:
        print('Введите диапазон индексов директорий, содержащих данные распределений или одиночный индекс:')
        ww_dir_range_str = input()
        return self._parse_range_str(ww_dir_range_str, stage_dir_indexes)

    @staticmethod
    def _parse_range_str(ww_dir_range_str: str, stage_dir_indexes: list) -> Union[list, None]:
        ww_dir_range_str_list = re.split(',+\s*', ww_dir_range_str)
        ww_dir_range_list = [None] * 3
        for ind, num_str in enumerate(ww_dir_range_str_list):
            if ind > 2:
                break
            if num_str.isnumeric():
                ww_dir_range_list[ind] = int(num_str)
            else:
                print('Wrong WW dirs range. Maybe not numeric values.')
                return None
        if ((ww_dir_range_list[0] in stage_dir_indexes or ww_dir_range_list[0] is None) and
                (ww_dir_range_list[1] in stage_dir_indexes or ww_dir_range_list[1] is None)):
            return ww_dir_range_list
        else:
            print(f'Wrong WW dirs range. Start or Stop values is out of range. '
                  f'start={ww_dir_range_list[0]}, stop={ww_dir_range_list[1]}')
            return None

    @staticmethod
    def _ww_range_to_list(ww_range: list, stage_data_indexes: list) -> List[int]:
        start, stop, step = ww_range
        if stop is None:
            ww_dir_indexes_list = [data_ind for data_ind in stage_data_indexes if start == data_ind]
        else:
            ww_dir_indexes_list = [data_ind for data_ind in stage_data_indexes if start <= data_ind <= stop][::step]
        return ww_dir_indexes_list

    def _check_command(self, input_string: str):
        if input_string.startswith('--'):
            if input_string == '--help':
                self._print_help()
                return 1
            elif input_string == '--ww':
                self._print_ww_descriptions()
                return 1
            elif input_string == '--extract':
                ww_folder_path = self._input_ww_folder_path()
                self.data_collector.extract_ww_data(ww_folder_path)
                return 1
            elif input_string == '--add':
                self.is_add_to_exists = True
                return 1
            elif input_string == '--log':
                self.is_log_scale = True
                return 1
            else:
                print('Wrong command.', end='\n\n')
                return -1
        elif not input_string.isnumeric():
            print('Wrong command or WW number.', end='\n\n')
            return -2
        else:
            return 0

    def _input_ww_folder_path(self, stage_name=''):
        ww_folder_path = None
        while not ww_folder_path:
            ww_folder_path = super(WWDataCmdUserInteractor, self)._input_ww_folder_path(stage_name)
        return ww_folder_path

    def _print_ww_descriptions(self):
        print(f'№{" " * 46}Описание')
        print(self.data_collector.descriptions['description'], end='\n\n')

    @staticmethod
    def _print_help():
        print(f'--help     Справка по всем командам.\n'
              f'--extract  Извлечь WW-файлы распределений из файлов промежуточных результатов.\n'
              f'--add      Добавить данные на существующий график.\n'
              f'--log      Установить логарифмическую шкалу по оси - y при создании графика.\n'
              f'--ww       Просмотр доступных номеров WW-файлов (распределений) и их описаний.', end='\n\n')

    @staticmethod
    def print_ww_dict(ww_data_dict: dict):
        for dir_ind, ww_data in ww_data_dict.items():
            print(f'{dir_ind}: {{')
            for ww_ind, ww_df in ww_data.items():
                print(f'{ww_ind:10}:')
                df_str = ww_df.to_string(max_rows=10)
                df_list = df_str.split('\n')
                indent = 11 * ' '
                df_list[0] = indent + df_list[0]
                df_indent = '\n' + indent
                df_format_str = df_indent.join(df_list)
                print(df_format_str)
                print('}\n')


class ExtractWorker(QObject):
    statusbar_message_signal = Signal(str)

    def __init__(self):
        super().__init__()

    @Slot(list)
    def extract_slot(self, extracting_paths_list):
        self.statusbar_message_signal.emit(f'Extracting...')
        for path in extracting_paths_list:
            WWDataCollector.extract_ww_data(data_folder_path=path)
        self.statusbar_message_signal.emit('Extraction done!')
        time.sleep(3)
        self.statusbar_message_signal.emit('')


class InterfaceDataManager(QObject):
    statusbar_message_signal = Signal(str)

    def __init__(self, user_interactor: WWDataUserInteractor):
        super().__init__()
        self.user_interactor = user_interactor

        self.extract_worker = ExtractWorker()
        self.extraction_thread = QThread()
        self.extract_worker.moveToThread(self.extraction_thread)
        self.extraction_thread.started.connect(self.extract_worker.extract_slot)
        self.extraction_thread.start()

    @Slot(dict)
    def plot_slot(self, plotting_dict: dict):
        # Set plot flags
        self.user_interactor.is_add_to_exists = plotting_dict['is_add']
        self.user_interactor.is_log_scale = plotting_dict['is_log']
        # Unpack plot variables
        ww_number = plotting_dict['ww_number']
        df_col_name = self.user_interactor.data_collector.descriptions['df_col_name'].loc[ww_number]
        # Plot data
        for stage_name, ww_dir_list in plotting_dict['dirs'].items():
            self.user_interactor.plot(stage_name=stage_name,
                                      ww_dir_numbers_list=ww_dir_list,
                                      ww_number=ww_number,
                                      df_col_name=df_col_name,
                                      backend='QtAgg')
            self.user_interactor.is_add_to_exists = True

    @Slot(list)
    def extract_slot(self, extracting_paths_list: list):
        self.statusbar_message_signal.emit(f'Extracting...')
        for path in extracting_paths_list:
            self.user_interactor.data_collector.extract_ww_data(data_folder_path=path)
        self.statusbar_message_signal.emit('Extraction done!')
        time.sleep(3)
        self.statusbar_message_signal.emit('')

    @Slot()
    def close_event_slot(self):
        self.extraction_thread.quit()
        pass


class WWDataInterfaceUserInteractor:
    def __init__(self, ww_data_collector: WWDataCollector):

        self.user_interactor = WWDataUserInteractor(ww_data_collector)
        self.data_manager = InterfaceDataManager(self.user_interactor)

    def run(self):
        app = QApplication()
        descriptions = self.user_interactor.data_collector.descriptions
        main_window = MainWindow(ww_descriptions=descriptions['description'],
                                 file_manager_root_path=self.user_interactor.data_collector.distributions_path)
        main_window.plot_signal.connect(self.data_manager.plot_slot)
        main_window.extract_signal.connect(self.data_manager.extract_worker.extract_slot)
        main_window.close_event_signal.connect(self.data_manager.close_event_slot)
        self.data_manager.extract_worker.statusbar_message_signal.connect(main_window.statusbar_message_slot)
        main_window.show()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()

