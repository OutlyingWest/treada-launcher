import os
import subprocess


def main():
    data_folder = input('Enter WW data folder name:')
    extract_ww_data(data_folder)


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


if __name__ == '__main__':
    main()
