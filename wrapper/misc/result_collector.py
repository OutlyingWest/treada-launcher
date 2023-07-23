import os
import re
import sys
import time
from typing import Union, Tuple
from pprint import pprint


all_result_regex = '^res_.*'
dark_result_regex = '^res_.*_dark.*'
light_result_regex = '^res_.*_light.*'

arg_dict = {
    '-a': all_result_regex,
    '-d': dark_result_regex,
    '-l': light_result_regex,
}

numeric_var_regex = r'(-?\d+\.\d+[eE]?-?\d+)'

var_names_dict = {
    # 'UDRM',
    # 'EMINI',
    # 'EMAXI',
    'TRANSIENT_TIME': numeric_var_regex,
    'TRANSIENT_CURRENT_DENSITY': numeric_var_regex,
    'LAST_MEAN_TIME': numeric_var_regex,
    'LAST_MEAN_DENSITY': numeric_var_regex,
}


def main():
    # Get command arg and result name regex by first command arg
    file_arg, result_regex = get_file_by_arg()

    # Set result path
    config = load_config('config.json')
    result_path = os.path.split(config.paths.output.result)[0] + os.sep

    # Get list of selected result names
    res_list = get_result_names(result_regex,
                                result_path=result_path)

    # Sort result names by Voltages
    sorted_res_list = sorted(res_list, key=extract_number)

    # Get var name and var regex by second command arg
    var_name, var_regex = get_var_by_arg()

    # Get list of selected var values
    var_list = extract_var_list(res_names_list=sorted_res_list,
                                var_name=var_name,
                                var_regex=var_regex,
                                result_path=result_path)

    # Save to file
    save_result(var_list, var_name, file_arg)


def get_file_by_arg() -> Tuple[str, str]:
    if len(sys.argv) > 1:
        for arg, regex in arg_dict.items():
            if sys.argv[1] == arg:
                file_arg = arg
                file_name_regex = regex
                break
        else:
            raise ValueError('Wrong command argument.')
    else:
        print('Set right command argument.')
        print(f'Available arguments: {", ".join(arg_dict.keys())}')
        raise ValueError('None first command argument.')
    return file_arg, file_name_regex


def get_var_by_arg() -> Tuple[str, str]:
    if len(sys.argv) > 2:
        for name, regex in var_names_dict.items():
            if sys.argv[2] == name:
                var_name = name
                var_clean_regex = regex
                break
        else:
            raise ValueError('Wrong command argument.')
    else:
        print('Set right command argument.')
        print(f'Available arguments: {", ".join(var_names_dict.keys())}')
        raise ValueError('None second command argument.')
    return var_name, var_clean_regex


def get_result_names(result_regex: str, result_path='.') -> list:
    res_file_names = os.listdir(result_path)
    res_list = list()
    for res_file_name in res_file_names:
        match = re.match(result_regex, res_file_name)
        if match:
            res_list.append(res_file_name)
    # print(res_list)
    return res_list


def extract_number(res_name: str) -> Union[float, None]:
    """
    Extract voltage from res_name string.
    :param res_name: res_name string
    :return: voltage in float or None if it does not found
    """
    match = re.search(r'(-?\d+\.\d+)', res_name)
    if match:
        return float(match.group(1))
    else:
        return None


def extract_var_list(res_names_list: list, var_name: str, var_regex: str, result_path='') -> list:
    var_list = list()
    print(f'{len(res_names_list)=}')
    for res_ind, res_name in enumerate(res_names_list):
        print(f'{res_ind:3}. {res_name}')
        file_manager = FileManager(result_path + res_name)
        file_manager.load_file_head(100)
        var_string = file_manager.get_var(var_name)
        var_match = re.search(var_regex, var_string)
        var_cleaned_string = var_match.group()
        var_list.append((res_name, var_cleaned_string.replace('.', ',') + '\n'))
    # pprint(var_list)
    return var_list


def save_result(var_list: list, var_name: str, file_arg: str):
    result_file_name = f'{var_name.lower()}{file_arg}.txt'
    print(f'{result_file_name=}')
    with open(result_file_name, 'w') as result_file:
        for _, var_value in var_list:
            result_file.write(var_value)


if __name__ == '__main__':
    # Add path to "wrapper" directory in environ variable - PYTHONPATH
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data", "..", "wrapper"))
    print(wrapper_path)
    sys.path.append(wrapper_path)
    from core.data_management import FileManager
    from config.config_builder import load_config
    main()
