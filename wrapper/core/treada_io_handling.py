import os
import sys
import subprocess
import time
import shutil
from typing import Union

from wrapper.config.config_build import Config
from wrapper.core.ending_conditions import retrieve_current_value
from wrapper.core import ending_conditions as ec
from wrapper.core.data_management import TransientOutputParser, MtutManager
from wrapper.launch.scenarios.scenario_build import StageData


def main():
    pass


class TreadaRunner:
    """
    Responsible for launch of "Treada" program.
    """
    old_mtut_time = None

    def __init__(self, config: Config, relative_time: float):
        self.config = config
        self.relative_time = relative_time
        temp_range = None
        if self.config.advanced_settings.runtime.distributions.enable_preserving_ranges:
            ranges = self.config.advanced_settings.runtime.distributions.preserving_ranges
            temp_range = self.apply_ranged_temporaries_dumping(self.relative_time, ranges,
                                                               self.config.paths.treada_core.mtut)
        self.temp_range = temp_range
        self.exec_process = self._exe_runner(exe_path=config.paths.treada_core.exe)
        self.capturer = StdoutCapturer(process=self.exec_process,
                                       config=config,
                                       relative_time=relative_time,)

    def run(self, stage_data: StageData, output_file_path='', is_show_stage_name=True):
        """
        Runs Treada's program working stage.
        :param output_file_path: path to raw Treada's program output file
        :param stage_data: Treada's working scenario stage data
        :param is_show_stage_name: Is show stage name in console
        """
        self.capturer.set_stage_data(stage_data, is_show_stage_name)
        if output_file_path:
            self.capturer.stream_management(self.temp_range, path_to_output=output_file_path)
        else:
            self.capturer.stream_management(self.temp_range)

    @staticmethod
    def _exe_runner(exe_path: str) -> subprocess.Popen:
        """
        Runs *.exe and returns itself like subprocess.Popen object.

        :param exe_path: Path to the executable program file
        :return: subprocess.Popen
        """
        try:
            working_directory_path = os.path.split(exe_path)[0]
            return subprocess.Popen(exe_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    cwd=working_directory_path, encoding='utf-8')
        except FileNotFoundError:
            print('Executable file not found, Path:', exe_path)

    def get_last_step_current(self) -> Union[float, None]:
        """
        Can be used only after run() function.
        """
        if self.capturer.last_step_string:
            return TransientOutputParser.get_single_current_from_line(self.capturer.last_step_string)
        else:
            return None

    @classmethod
    def apply_ranged_temporaries_dumping(cls, rel_time: float, ranges: dict,
                                         mtut_file_path: str) -> Union[dict, None]:
        """
        Calculate and set variable TIME in MTUT file, which responsible for period of dumping temporary results to
        hard disk. That performs in accordance with set time range from config.json
        :param rel_time: previously calculated relative time
        :param ranges: time ranges from config.json, where (start, stop, step) are set in picoseconds
        :param mtut_file_path: path to MTUT
        :returns: corrected temp_range, old TIME variable value
        """
        mtut_manager = MtutManager(mtut_file_path)
        mtut_manager.load_file()
        stage_number = mtut_manager.get_var('CKLKRS').rstrip('.')
        temp_range = None
        if stage_number in ranges.keys():
            temp_range = ranges[stage_number]
            if temp_range['start'] >= temp_range['stop']:
                raise ValueError('"stop" must be higher than "start" in "time_ps_range"')
            if temp_range['step'] > temp_range['stop']:
                temp_range['step'] = temp_range['stop']
            cls.old_mtut_time = mtut_manager.get_var('TIME')
            operating_timestep = float(mtut_manager.get_var('TSTEP'))
            timestep_constant = calculate_timestep_constant(operating_timestep, rel_time)
            mtut_time = str(int(temp_range['step'] / timestep_constant))
            mtut_manager.set_var('TIME', mtut_time)
        elif cls.old_mtut_time:
            mtut_manager.set_var('TIME', cls.old_mtut_time)
        else:
            cls.old_mtut_time = mtut_manager.get_var('TIME')
        mtut_manager.save_file()
        return temp_range


def calculate_timestep_constant(operating_time_step: float, relative_time: float) -> float:
    """Calculate timestep constant"""
    time_step_const = operating_time_step * relative_time
    return time_step_const


class StdoutCapturer:
    def __init__(self, process: subprocess.Popen, config: Config, relative_time: float):
        # Running of the executable file
        self.process = process
        # Init auto ending prerequisites
        self.is_auto_ending = config.options.auto_ending
        condition_params = config.advanced_settings.runtime.ending_condition
        self.ending_condition = ec.EndingCondition(chunk_size=condition_params.chunk_size,
                                                   equal_values_to_stop=condition_params.equal_values_to_stop,
                                                   deviation_coef=condition_params.deviation)
        # self.ending_condition = LineEndingCondition(precision=1e-2,
        #                                             chunk_size=100,
        #                                             big_step_multiplier=100,
        #                                             low_step_border=100)
        # self.ending_condition = MeansEndingCondition(precision=2e-5,
        #                                              chunk_size=100,
        #                                              big_step_multiplier=100,
        #                                              low_step_border=100)
        # Flag for enable capacity info collecting mode
        self.is_capacity_info_collecting = False
        # Distributions variables:
        # Preserve temporary Treada's files flag
        self.is_preserve_temp_distributions = config.options.preserve_distributions
        self.distribution_dumping_begins = False
        if self.is_preserve_temp_distributions:
            self.stage_name = ''
            self.distribution_filenames = config.distribution_filenames
            self.distribution_initial_path = os.path.split(config.paths.treada_core.exe)[0]
            self.distribution_destination_path = config.paths.result.temporary.distributions
            self.is_distribution_range_enabled = config.advanced_settings.runtime.distributions.enable_preserving_ranges
            self.distribution_range = None
        else:
            self.is_distribution_range_enabled = None

            # Can be defined by setter
        self.runtime_console_info = ''

        # Time variables:
        self.relatives_found = False
        self.relative_time = relative_time
        mtut_vars: dict = self.load_current_mtut_vars(config.paths.treada_core.mtut)
        operating_time_step = mtut_vars['TSTEP']
        self.timestep_constant = calculate_timestep_constant(operating_time_step, relative_time)

        # transient time calculation variables:
        self.is_consider_fixed_light_time = config.advanced_settings.runtime.light_impulse.consider_fixed_time
        self.is_consider_fixed_dark_time = config.advanced_settings.runtime.dark_impulse.consider_fixed_time

        self.ilumen = mtut_vars['ILUMEN']
        self.stage_number = mtut_vars['CKLKRS']

        if self.is_consider_fixed_light_time:
            self.light_impulse_time_ps = config.advanced_settings.runtime.light_impulse.fixed_time_ps

        self.stage_number = mtut_vars['CKLKRS']
        if self.is_consider_fixed_dark_time:
            if self.stage_number not in config.advanced_settings.runtime.dark_impulse.for_stages:
                self.is_consider_fixed_dark_time = False
            else:
                self.dark_impulse_time_ps = config.advanced_settings.runtime.dark_impulse.fixed_time_ps

        # io_loop variables:
        self.running_flag = True
        self.is_currents_line = False
        self.str_counter = 0
        if self.stage_number < 2:
            self.currents_str_counter = 0
        else:
            # In case if stage is not first (Because the last value from previous stage preserves on such stages' dfs)
            self.currents_str_counter = 1
        self.last_step_string = None

    def stream_management(self, temp_range: Union[dict, None], path_to_output=None):
        """
        Divides data from *.exe stdout to its own stdout and file with name *_output.txt.
        Ends by KeyboardInterrupt or ending condition satisfaction
        """
        if self.is_distribution_range_enabled and temp_range:
            temp_range['stop'] = temp_range['stop'] + self.timestep_constant
            self.distribution_range = temp_range
        # Strip slashes if only file name was used as a path (for solving of powershell issues)
        if path_to_output:
            if path_to_output.count(os.path.sep) <= 2:
                path_to_output = path_to_output.strip(os.path.sep)
                path_to_output = f'{path_to_output.split(".")[0]}_raw_output.txt'
        self.capacity_info_stage_automatic_input()
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

        start_time = time.time()
        while self.running_flag:
            try:
                if num_of_str and num_of_str <= self.str_counter:
                    break
                try:
                    # Get line from process object
                    treada_output: str = self.process.stdout.readline()
                except UnicodeDecodeError as e:
                    treada_output = ''
                    print(e)
                if treada_output == '' and self.process.poll() is not None:
                    break
                if treada_output:
                    printable_output = treada_output.strip('\n')
                    clean_output = treada_output.lstrip(' ')
                    self.conditional_io_loop_features(clean_output)
                    # Copy *.exe output to its own stdout
                    print(printable_output + self.runtime_console_info)
                    # Write *.exe output to file
                    if output_file:
                        output_file.write(clean_output)
                    self.str_counter += 1
            except KeyboardInterrupt:
                self.running_flag = False

        end_time = time.time()
        execution_time = end_time - start_time
        print('Number of strings:', self.str_counter)
        print(f'Execution time in I/O loop:{execution_time:.2f}s')

    async def keyboard_catch(self):
        pass

    def capacity_info_stage_automatic_input(self):
        """
        For capacity_scenario on "capacity_info" stage only.
        If auto_ending option: true, inputs Enter button commands to Treada's stdin automatically.
        :return:
        """
        if self.is_capacity_info_collecting and self.is_auto_ending:
            for _ in range(100):
                try:
                    self.process.stdin.write('\n')
                    self.process.stdin.flush()
                except OSError:
                    break

    def set_stage_data(self, stage: StageData, is_show_stage_name=True):
        if is_show_stage_name:
            self.set_runtime_console_info(f'   {stage.name}')
        self.is_capacity_info_collecting = stage.is_capacity_info_collecting
        self.stage_name = stage.name

    def set_runtime_console_info(self, info: str):
        self.runtime_console_info = info.title()

    def conditional_io_loop_features(self, clean_decoded_output):
        if self.is_capacity_info_collecting:
            pass
        else:
            self.transient_io_loop_features(clean_decoded_output)

    def transient_io_loop_features(self, clean_decoded_output):
        current_value = retrieve_current_value(currents_string=clean_decoded_output)
        if current_value:
            self.is_currents_line = True
        else:
            self.is_currents_line = False
        # Check ending condition of transient process
        if self.is_auto_ending:
            if self.is_currents_line and self.ending_condition.check(current_value):
                self.running_flag = False
        current_transient_time = self.calculate_current_transient_time()
        if self.is_preserve_temp_distributions:
            self.preserve_distributions(current_transient_time, output_string=clean_decoded_output)
        if self.is_consider_fixed_light_time:
            self.check_light_impulse_time_condition(current_transient_time,
                                                    self.light_impulse_time_ps,
                                                    self.ilumen)
        if self.is_consider_fixed_dark_time:
            self.check_dark_impulse_time_condition(current_transient_time,
                                                   self.dark_impulse_time_ps,
                                                   self.ilumen)
        # Pure current lines' indexes counting
        if self.is_currents_line:
            self.currents_str_counter += 1  # increment must be after all additional loop conditions
            # Preserve last step's string
            self.last_step_string = clean_decoded_output

    def capacity_io_loop_features(self, clean_decoded_output):
        pass

    def preserve_distributions(self, transient_time: float, output_string: str):
        """
        Preserve distributions of several values that contain in Treada's temporary files.
        :return:
        """
        if self.is_distribution_range_enabled and self.distribution_range:
            if not self.distribution_range['start'] <= transient_time <= self.distribution_range['stop']:
                return
        # Find the beginning line of temporary results dumping info
        if not self.is_currents_line:
            if (TransientOutputParser.temporary_results_line_found(output_string) and
               not self.distribution_dumping_begins):
                self.distribution_dumping_begins = True
        if self.distribution_dumping_begins:
            # Check has dumping already ended
            if self.is_currents_line:
                self.distribution_dumping_begins = False
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
        if self.str_counter > 500:
            raise ValueError('Error: RELATIVE TIME not found on runtime. Maybe EN language not enabled in MTUT file')
        return relative_time

    @staticmethod
    def load_current_mtut_vars(mtut_file_path: str) -> dict:
        mtut_manager = MtutManager(mtut_file_path)
        mtut_manager.load_file()
        mtut_vars = {
            'TSTEP': float(mtut_manager.get_var('TSTEP')),
            'ILUMEN': float(mtut_manager.get_var('ILUMEN')),
            'CKLKRS': float(mtut_manager.get_var('CKLKRS')),
        }
        return mtut_vars

    def calculate_current_transient_time(self) -> Union[float, None]:
        # TODO: Fix the wrong calc. of current transient time for the first stage cause the initial timestep is on that
        current_transient_time = self.currents_str_counter * self.timestep_constant
        return current_transient_time

    def check_light_impulse_time_condition(self, current_transient_time: float,
                                           light_impulse_time: float,
                                           ilumen: float):
        if current_transient_time > light_impulse_time and ilumen and not self.distribution_dumping_begins:
            print('Stopped by fixed light impulse time condition.')
            self.running_flag = False
        elif not self.running_flag and ilumen:
            self.running_flag = True

    def check_dark_impulse_time_condition(self, current_transient_time: float,
                                          dark_impulse_time: float,
                                          ilumen: float):
        if current_transient_time > dark_impulse_time and not ilumen and not self.distribution_dumping_begins:
            print('Stopped by fixed dark impulse time condition.')
            self.running_flag = False
        elif not self.running_flag and not ilumen:
            self.running_flag = True


if __name__ == '__main__':
    # Add path to "wrapper" directory in environ variable - PYTHONPATH
    wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(wrapper_path)
    from misc.global_functions import create_dir
    main()
else:
    from wrapper.misc.global_functions import create_dir, read_line_from_file_end
