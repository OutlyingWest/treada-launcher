import asyncio
import sys
import subprocess
import time
import keyboard


async def main():
    path_to_executable = sys.argv[1]
    exec_process = exe_runner(exe_path=path_to_executable)
    capturer = StdoutCapturer(process=exec_process)
    output_path = path_to_executable.strip('. ').split('.')[0]

    # Tasks for asynchronous execution
    tasks = [
        capturer.stream_manage(path_to_txt=output_path),
        # capturer.wait_configer.shortcut_wait(),
    ]
    await asyncio.gather(*tasks)


def exe_runner(exe_path: str) -> subprocess.Popen:
    """
    Runs *.exe and returns itself like subprocess.Popen object.

    :param exe_path: Path to the executable program file
    :return: subprocess.Popen
    """
    return subprocess.Popen(exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class KeyboardWaitConfiger:
    def __init__(self, shortcut: str):
        self.keyboard_shortcut = shortcut
        self.running_flag = True
        keyboard.add_hotkey(self.keyboard_shortcut, self.on_push_shortcut)

    @staticmethod
    async def shortcut_wait():
        keyboard.wait()

    def on_push_shortcut(self):
        self.running_flag = False


class StdoutCapturer:
    def __init__(self, process: subprocess.Popen):
        # Running of the executable file
        self.process = process
        # Shut down shortcut configure
        self.running_flag = True
        # self.wait_configer = KeyboardWaitConfiger('ctrl+x')

    async def stream_manage(self, path_to_txt: str):
        """
        Divides data from *.exe stdout to its own stdout and file with name *_output.txt.
        """
        str_counter = 0
        num_of_str = int(sys.argv[2])

        # Strip slashes if only file name was used as a path (for solving of powershell issues)
        if path_to_txt.count('/') <= 2 or path_to_txt.count('\\') <= 2:
            path_to_txt = path_to_txt.strip('/\\')

        with open(f'{path_to_txt.split(".")[0]}_output.txt', "w") as output_file:
            start_time = time.time()
            while num_of_str > str_counter and self.running_flag:
                try:
                    # Get line from process object
                    treada_output: bytes = self.process.stdout.readline()
                    if treada_output == b'' and self.process.poll() is not None:
                        break
                    if treada_output:
                        try:
                            decoded_output = treada_output.decode('utf-8')
                            # Write *.exe output to file
                            output_file.write(decoded_output.rstrip('\n'))
                        except UnicodeDecodeError:
                            decoded_output = treada_output
                        # Copy *.exe output to its own stdout
                        print(decoded_output.strip())
                        str_counter += 1
                except KeyboardInterrupt:
                    self.running_flag = False

            end_time = time.time()
            # Terminate main executable process
            self.process.terminate()

        execution_time = end_time - start_time
        print('Number of strings:', str_counter)
        print(f'Execution time:{execution_time:.2f}s')
        # Errors' catching
        error = self.process.stderr.read().decode('utf-8')
        if error:
            print('ERRORS:', error.strip())

    async def keyboard_catch(self):
        pass

    async def ending_condition_check(self):
        pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete((main()))
