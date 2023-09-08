import os
import sys
import subprocess
import time
import shutil
from typing import Union

import numpy as np

from wrapper.config.config_builder import Config
from wrapper.core.ending_conditions import current_value_prepare
from wrapper.core import ending_conditions as ec
from wrapper.core.data_management import TreadaOutputParser, MtutManager


def main():
    path_to_executable = sys.argv[1]
    runner = TreadaRunner
    exec_process = runner.exe_runner(exe_path=path_to_executable)
    capturer = StdoutCapturer(process=exec_process)
    output_path = path_to_executable.strip('. ').split('.')[0]
    capturer.stream_management(path_to_output=output_path)


class TreadaRunner:
    """
    Responsible for launch of "Treada" program.
    """
    def __init__(self, config):
        self.exec_process = self._exe_runner(exe_path=config.paths.treada_core.exe)
        self.capturer = StdoutCapturer(process=self.exec_process,
                                       config=config,
                                       ending_condition_params=None)

    def run(self, output_file_path='', stage_name='None Stage'):
        """
        Runs Treada's program working stage.
        :param output_file_path: path to raw Treada's program output file
        :param stage_name: Treada's working stage name
        """
        self.capturer.set_stage_name(stage_name)
        self.capturer.set_runtime_console_info(f'   {stage_name}')
        if output_file_path:
            self.capturer.stream_management(path_to_output=output_file_path)
        else:
            self.capturer.stream_management()

    @staticmethod
    def _exe_runner(exe_path: str) -> subprocess.Popen:
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

    def get_last_step_current(self) -> Union[float, None]:
        """
        Can be used only after run() function.
        """
        if self.capturer.last_step_string:
            return TreadaOutputParser.get_single_current_from_line(self.capturer.last_step_string)
        else:
            return None


class StdoutCapturer:
    def __init__(self, process: subprocess.Popen,
                 ending_condition_params,
                 config: Config,
                 is_preserve_temp_distributions=False):
        # Running of the executable file
        self.process = process
        # io_loop variables:
        self.running_flag = True
        self.str_counter = 0
        self.currents_str_counter = 0
        # Init auto ending prerequisites
        self.auto_ending = config.flags.auto_ending
        self.ending_condition = ec.EndingCondition(chunk_size=500,
                                                   equal_values_to_stop=5,
                                                   deviation_coef=1e-5)
        # self.ending_condition = LineEndingCondition(precision=1e-2,
        #                                             chunk_size=100,
        #                                             big_step_multiplier=100,
        #                                             low_step_border=100)
        # self.ending_condition = MeansEndingCondition(precision=2e-5,
        #                                              chunk_size=100,
        #                                              big_step_multiplier=100,
        #                                              low_step_border=100)

        # Distributions variables:
        # Preserve temporary Treada's files flag
        self.is_preserve_temp_distributions = config.flags.preserve_distributions
        if self.is_preserve_temp_distributions:
            self.stage_name = ''
            self.temporary_dumping_begins = False
            self.distribution_filenames = config.distribution_filenames
            self.distribution_initial_path = os.path.split(config.paths.treada_core.exe)[0]
            self.distribution_destination_path = config.paths.result.temporary.distributions

        # Can be defined by setter
        self.runtime_console_info = ''

        # Relative time variables:
        self.is_find_relative_time = config.advanced_settings.runtime.find_relative_time
        self.relatives_found = False
        self.relative_time: Union[None, float] = None

        # transient time calculation variables:
        self.is_consider_fixed_light_time = config.advanced_settings.runtime.light_impulse.consider_fixed_time
        if self.is_consider_fixed_light_time:
            mtut_vars: dict = self.load_current_mtut_vars(config.paths.treada_core.mtut)
            self.operating_time_step = mtut_vars['TSTEP']
            self.ilumen = mtut_vars['ILUMEN']
            self.timestep_constant: Union[None, float] = None
            self.light_impulse_time_ps = config.advanced_settings.runtime.light_impulse.fixed_time_ps
        self.light_impulse_time_condition = False
        self.last_step_string = None

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

        if len(sys.argv) > 2:
            num_of_str = int(sys.argv[2])
        else:
            num_of_str = None

        clean_decoded_output = None
        start_time = time.time()
        while self.running_flag:
            try:
                if num_of_str and num_of_str <= self.str_counter:
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
                                current_value_prepare(currents_string=clean_decoded_output)
                            )
                            # if current_value and self.ending_condition.check(self.str_counter, current_value):
                            if current_value and self.ending_condition.check(current_value):
                                self.running_flag = False
                        if self.is_preserve_temp_distributions:
                            self.preserve_distributions(output_string=clean_decoded_output)
                        if self.is_find_relative_time:
                            if not self.relative_time:
                                self.relative_time = self.runtime_find_relative_time(output_string=clean_decoded_output)
                            if self.relative_time:
                                # Check fixed light impulse time condition
                                if self.is_consider_fixed_light_time:
                                    transient_time = self.get_current_transient_time(self.relative_time)
                                    if self.check_light_impulse_time_condition(transient_time,
                                                                               self.light_impulse_time_ps,
                                                                               self.ilumen):
                                        self.running_flag = False
                        # Pure current lines' indexes counting
                        if self.is_preserve_temp_distributions or self.is_find_relative_time:
                            if TreadaOutputParser.keep_currents_line_regex(string=clean_decoded_output):
                                self.currents_str_counter += 1  # increment must be after all additional loop conditions

                        # Write *.exe output to file
                        if output_file:
                            output_file.write(clean_decoded_output)
                    except UnicodeDecodeError:
                        decoded_output = treada_output
                    # Copy *.exe output to its own stdout
                    print(decoded_output.rstrip() + self.runtime_console_info)
                    self.str_counter += 1
            except KeyboardInterrupt:
                self.running_flag = False

        end_time = time.time()
        execution_time = end_time - start_time
        print('Number of strings:', self.str_counter)
        print(f'Execution time in I/O loop:{execution_time:.2f}s')
        # Preserve last step string
        self.last_step_string = clean_decoded_output


    async def keyboard_catch(self):
        pass

    def set_runtime_console_info(self, info: str):
        self.runtime_console_info = info.title()

    def set_stage_name(self, stage_name: str):
        self.stage_name = stage_name

    def preserve_distributions(self, output_string: str):
        """
        Preserve distributions of several values that contain in Treada's temporary files.
        :return:
        """
        # Find the beginning line of temporary results dumping info
        if (TreadaOutputParser.temporary_results_line_found(output_string) and
           not self.temporary_dumping_begins):
            print(f'{output_string=}')
            self.temporary_dumping_begins = True
        if self.temporary_dumping_begins:
            # Check is dumping has ended
            if TreadaOutputParser.keep_currents_line_regex(output_string):
                self.temporary_dumping_begins = False
                print(f'{self.currents_str_counter=}')
                self.copy_distribution_files()

    def copy_distribution_files(self):
        """
        Preserve Treada's temporary files that are generated and rewritten
        on runtime to "result/temporary/distributions" directory.
        :return:
        """
        extracted_distributions_dir_path = os.path.join(
            self.distribution_destination_path, self.stage_name, str(self.currents_str_counter), ''
        )
        print(f'{extracted_distributions_dir_path=}')
        create_dir(extracted_distributions_dir_path)
        for dist_file_name in self.distribution_filenames:
            dist_initial_file_path = os.path.join(self.distribution_initial_path, dist_file_name)
            dist_destination_file_path = os.path.join(extracted_distributions_dir_path, dist_file_name)
            shutil.copy(dist_initial_file_path, dist_destination_file_path)

    def runtime_find_relative_time(self, output_string: str) -> Union[float, None]:
        relative_time = None
        if output_string.startswith('RELATIVE UNITES:'):
            self.relatives_found = True
        if self.relatives_found and output_string.startswith('TIME:'):
            relative_time = float((output_string.split(' ')[2]))
            print(f'{relative_time=}')
            # input()
        if self.str_counter > 500:
            raise ValueError('Error: RELATIVE TIME not found on runtime. Maybe EN language not enabled in MTUT file')
        return relative_time

    @staticmethod
    def load_current_mtut_vars(mtut_file_path: str) -> dict:
        # Get operating time step from MTUT file
        mtut_manager = MtutManager(mtut_file_path)
        mtut_manager.load_file()
        mtut_vars = {
            'TSTEP': float(mtut_manager.get_var('TSTEP')),
            'ILUMEN': float(mtut_manager.get_var('ILUMEN')),
        }
        return mtut_vars

    @staticmethod
    def find_timestep_constant(operating_time_step: float, relative_time: float) -> float:
        # Calculate timestep constant
        time_step_const = operating_time_step * relative_time
        return time_step_const

    def get_current_transient_time(self, relative_time: float) -> Union[float, None]:
        current_transient_time = None
        if not self.timestep_constant:
            self.timestep_constant = self.find_timestep_constant(self.operating_time_step, relative_time)
        if self.timestep_constant:
            current_transient_time = self.currents_str_counter * self.timestep_constant
        return current_transient_time

    def check_light_impulse_time_condition(self, current_transient_time: float,
                                           light_impulse_time: float,
                                           ilumen: float):
        if current_transient_time > light_impulse_time and ilumen:
            return True
        elif not self.running_flag and ilumen:
            self.running_flag = True
            return False


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
    from misc.global_functions import create_dir

    main()
else:
    from wrapper.misc.global_functions import create_dir


