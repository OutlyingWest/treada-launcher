import os
import sys
import subprocess
import time


def main():
    path_to_executable = sys.argv[1]
    exec_process = exe_runner(exe_path=path_to_executable)
    capturer = StdoutCapturer(process=exec_process)
    output_path = path_to_executable.strip('. ').split('.')[0]
    capturer.stream_management(path_to_txt=output_path)


def treada_runner(config, stage: int):
    exec_process = exe_runner(exe_path=config.paths.treada_exe)
    capturer = StdoutCapturer(process=exec_process)
    output_path = os.path.split(config.paths.treada_exe)[0]
    if stage == 'light_off':
        capturer.stream_management()
    elif stage == 'light_on':
        capturer.stream_management(path_to_txt=output_path)
    else:
        raise ValueError(f'Incorrect stage number: {stage}')


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

    def stream_management(self, path_to_txt=None):
        """
        Divides data from *.exe stdout to its own stdout and file with name *_output.txt.
        Ends by KeyboardInterrupt or ending condition satisfaction
        """

        # Strip slashes if only file name was used as a path (for solving of powershell issues)
        if path_to_txt:
            if path_to_txt.count('/') <= 2 or path_to_txt.count('\\') <= 2:
                path_to_txt = path_to_txt.strip('/\\')

        if not path_to_txt:
            self.__io_loop()
        else:
            with open(f'{path_to_txt.split(".")[0]}_raw_output.txt', "w") as output_file:
                self.__io_loop(output_file)

        # Terminate main executable process
        self.process.terminate()
        # Errors' catching
        error = self.process.stderr.read().decode('utf-8')
        if error:
            print('ERRORS:', error.strip())

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
                            output_file.write(decoded_output.rstrip('\n'))
                    except UnicodeDecodeError:
                        decoded_output = treada_output
                    # Copy *.exe output to its own stdout
                    print(decoded_output.strip())
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
