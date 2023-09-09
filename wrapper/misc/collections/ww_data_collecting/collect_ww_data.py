import os
from typing import Dict

import pandas as pd


def construct_ww_folder_path(stage_dir_name: str, ww_dir_index: int, ww_file_ind: int) -> str:
    ww_file_name = f'WW{ww_file_ind}.DAT'
    relative_ww_data_path = os.path.join(stage_dir_name, str(ww_dir_index), ww_file_name)
    return relative_ww_data_path


def load_ww_data(abs_res_path: str, stage_dir_name: str, ww_dir_indexes: list, ww_aliases: Dict[int, str]) -> dict:
    ww_data_dict = {}
    for ww_dir_index in ww_dir_indexes:
        ww_dir_index = int(ww_dir_index)
        ww_data_dict[ww_dir_index] = {}
        for ww_file_ind, ww_name in ww_aliases.items():
            relative_ww_data_path = construct_ww_folder_path(stage_dir_name, ww_dir_index, ww_file_ind)
            full_ww_path = os.path.join(abs_res_path, relative_ww_data_path)
            # Index in extracted from data_folder paths list
            ww_dataframe = pd.read_csv(full_ww_path, sep='\s+')
            ww_dataframe.columns = ['x', 'y', ww_name]
            # Discard tail
            ww_dataframe = ww_dataframe.loc[ww_dataframe['y'] == 0.]
            ww_data_dict[ww_dir_index][ww_file_ind] = ww_dataframe

        # print(f'{data_folders_dict[data_folder_name][list_ind]=}')
    return ww_data_dict


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

