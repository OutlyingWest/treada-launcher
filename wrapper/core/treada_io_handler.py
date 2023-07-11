import os
import sys
import subprocess
import time
from typing import Union
import numpy as np


def main():
    path_to_executable = sys.argv[1]
    runner = TreadaSwitcher
    exec_process = runner.exe_runner(exe_path=path_to_executable)
    capturer = StdoutCapturer(process=exec_process)
    output_path = path_to_executable.strip('. ').split('.')[0]
    capturer.stream_management(path_to_output=output_path)


class TreadaSwitcher:
    """
    Responsible for stages switching of "Treada" work
    """
    def __init__(self, config):
        self.exec_process = self.exe_runner(exe_path=config.paths.treada_core.exe)
        self.capturer = StdoutCapturer(process=self.exec_process, auto_ending=config.flags.auto_ending)

    def light_off(self):
        self.capturer.set_runtime_console_info('   Dark')
        self.capturer.stream_management()

    def light_on(self, output_file_path: str):
        self.capturer.set_runtime_console_info('   Light')
        self.capturer.stream_management(path_to_output=output_file_path)

    @staticmethod
    def exe_runner(exe_path: str) -> subprocess.Popen:
        """
        Runs *.exe and returns itself like subprocess.Popen object.

        :param exe_path: Path to the executable program file
        :return: subprocess.Popen
        """
        try:
            working_directory_path = os.path.split(exe_path)[0]
            return subprocess.Popen(exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    cwd=working_directory_path)
        except FileNotFoundError:
            print('Executable file not found, Path:', exe_path)


class StdoutCapturer:
    def __init__(self, process: subprocess.Popen, auto_ending=False):
        # Running of the executable file
        self.process = process
        # Shut down shortcut configure
        self.running_flag = True
        # Init auto ending prerequisites
        self.auto_ending = auto_ending
        self.ending_condition = EndingCondition(chunk_size=10000,
                                                equal_values_to_stop=100,
                                                deviation_coef=1e-5)
        self.runtime_console_info = ''

    def stream_management(self, path_to_output=None):
        """
        Divides data from *.exe stdout to its own stdout and file with name *_output.txt.
        Ends by KeyboardInterrupt or ending condition satisfaction
        """
        # Strip slashes if only file name was used as a path (for solving of powershell issues)
        if path_to_output:
            if path_to_output.count(os.path.sep) <= 2:
                path_to_output = path_to_output.strip(os.path.sep)
                path_to_output = f'{path_to_output.split(".")[0]}_raw_output.txt'

        if not path_to_output:
            self.__io_loop()
        else:
            # Creates output dir if it does not exist
            create_dir(path_to_output)

            with open(path_to_output, "w") as output_file:
                self.__io_loop(output_file)

        # Terminate main executable process
        self.process.terminate()

    def __io_loop(self, output_file=None):

        str_counter = 0
        if len(sys.argv) > 2:
            num_of_str = int(sys.argv[2])
        else:
            num_of_str = None

        start_time = time.time()
        while self.running_flag:
            try:
                if num_of_str and num_of_str <= str_counter:
                    break
                # Get line from process object
                treada_output: bytes = self.process.stdout.readline()
                if treada_output == b'' and self.process.poll() is not None:
                    break
                if treada_output:
                    try:
                        decoded_output = treada_output.decode('utf-8')
                        clean_decoded_output = decoded_output.strip('\n ')
                        # Check ending condition
                        if self.auto_ending:
                            current_value = (
                                self.ending_condition.current_value_prepare(currents_string=clean_decoded_output)
                            )
                            if current_value and self.ending_condition.check(current_value):
                                self.running_flag = False
                        # Write *.exe output to file
                        if output_file:
                            output_file.write(clean_decoded_output)
                    except UnicodeDecodeError:
                        decoded_output = treada_output
                    # Copy *.exe output to its own stdout
                    print(decoded_output.rstrip() + self.runtime_console_info)
                    str_counter += 1
            except KeyboardInterrupt:
                self.running_flag = False

        end_time = time.time()
        execution_time = end_time - start_time
        print('Number of strings:', str_counter)
        print(f'Execution time in I/O loop:{execution_time:.2f}s')

    async def keyboard_catch(self):
        pass

    def set_runtime_console_info(self, info: str):
        self.runtime_console_info = info


class EndingCondition:
    """
    Describe the logic of ending condition to stop "Treada's" work stage.
    """
    def __init__(self, chunk_size: int, equal_values_to_stop: int, deviation_coef: float):
        # Chunk vector init
        self.chunk: np.ndarray = np.zeros(chunk_size)
        self.chunk_size = chunk_size
        self.chunk_index = 0
        # Vector of mean values of each chunk init
        self.chunks_means_vector = np.zeros(equal_values_to_stop)
        self.means_vector_index = 0
        self.equal_values_to_stop = equal_values_to_stop
        self.deviation_coef = deviation_coef

    @staticmethod
    def current_value_prepare(currents_string: str) -> Union[float, None]:
        """
        Prepare raw "Treada's" output string to following operations.

        :param currents_string: raw "Treada's" output string
        :return: source current value (from first column of "Treada's" output)
        """
        currents_list = currents_string.split(' ')
        length_current_list = len(currents_list)
        if length_current_list == 12 or length_current_list == 13:
            try:
                float(currents_list[3])
                return float(currents_list[0])
            except ValueError:
                return None

    @staticmethod
    def is_equal(vector: np.ndarray, deviation: float) -> bool:
        """
        Check is all elements of vector lie in range of deviation.

        :param vector:
        :param deviation:
        :return:
        """
        difference = np.ptp(vector)
        if difference < 2*deviation:
            print(f'{difference=}')
            print(f'{2*deviation=}')
            return True
        elif -1e-10 < np.amax(vector) < 1e-10:
            print('Stopped by null condition.')
            return True
        else:
            return False

    def deviation(self):
        max_abs_mean = np.amax(np.abs(self.chunks_means_vector))
        deviation = max_abs_mean * self.deviation_coef
        return deviation

    def check(self, source_current: float) -> bool:
        """
        Checks ending condition.

        :param source_current: source current value (from first column of "Treada's" output)
        :return: True if condition is satisfied, False if it is not.
        """
        if self.chunk_index < self.chunk.size:
            self.chunk[self.chunk_index] = source_current
            self.chunk_index += 1
        else:
            self.chunk_index = 0
            self.chunks_means_vector[self.means_vector_index] = np.mean(self.chunk)

            if self.means_vector_index >= self.chunks_means_vector.size - 1:
                deviation_value = self.deviation()
                if self.is_equal(self.chunks_means_vector, deviation_value):
                    return True
                else:
                    self.chunks_means_vector = np.roll(self.chunks_means_vector, shift=-1)
                    self.means_vector_index -= 1
            else:
                self.means_vector_index += 1
        return False


if __name__ == '__main__':
    # Add path to "wrapper" directory in environ variable - PYTHONPATH
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(wrapper_path)
    from global_functions import create_dir

    main()
else:
    from wrapper.global_functions import create_dir


