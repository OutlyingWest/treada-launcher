import os
import sys
import subprocess
import time

from wrapper.global_functions import create_dir


def main():
    path_to_executable = sys.argv[1]
    runner = TreadaRunner
    exec_process = runner.exe_runner(exe_path=path_to_executable)
    capturer = StdoutCapturer(process=exec_process)
    output_path = path_to_executable.strip('. ').split('.')[0]
    capturer.stream_management(path_to_output=output_path)


class TreadaRunner:
    def __init__(self, exe_path: str):
        self.exec_process = self.exe_runner(exe_path=exe_path)
        self.capturer = StdoutCapturer(process=self.exec_process)

    def light_off(self):
        self.capturer.stream_management()

    def light_on(self, output_file_path: str):
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
    def __init__(self, process: subprocess.Popen):
        # Running of the executable file
        self.process = process
        # Shut down shortcut configure
        self.running_flag = True

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

        # Errors' catching
        error = self.process.stderr.read().decode('utf-8')
        if error:
            print('ERRORS:', error.strip())

        # Terminate main executable process
        self.process.terminate()

    def __io_loop(self, output_file=None):

        str_counter = 0
        if sys.argv[1:]:
            num_of_str = int(sys.argv[2])
        else:
            num_of_str = None

        start_time = time.time()
        while self.running_flag:
            try:
                if num_of_str and num_of_str > str_counter:
                    break
                # Get line from process object
                treada_output: bytes = self.process.stdout.readline()
                if treada_output == b'' and self.process.poll() is not None:
                    break
                if treada_output:
                    try:
                        decoded_output = treada_output.decode('utf-8')
                        # Write *.exe output to file
                        if output_file:
                            output_file.write(decoded_output.strip('\n '))
                    except UnicodeDecodeError:
                        decoded_output = treada_output
                    # Copy *.exe output to its own stdout
                    print(decoded_output.rstrip())
                    str_counter += 1
            except KeyboardInterrupt:
                self.running_flag = False

        end_time = time.time()
        execution_time = end_time - start_time
        print('Number of strings:', str_counter)
        print(f'Execution time in I/O loop:{execution_time:.2f}s')

    async def keyboard_catch(self):
        pass

    async def ending_condition_check(self):
        pass


if __name__ == '__main__':
    main()
