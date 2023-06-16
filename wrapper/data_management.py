import re
from wrapper.config_builder import Config


class MtutStageConfiger:
    def __init__(self, config: Config):
        self.config = config
        self.mtut_manager = MtutManager(self.config.paths.mtut)

    def light_off(self):
        for key, value in self.config.stages.light_off.items():
            self.mtut_manager.set_var(key, value)
        self.mtut_manager.save_file()

    def light_on(self):
        for key, value in self.config.stages.light_on.items():
            self.mtut_manager.set_var(key, value)
        self.mtut_manager.save_file()


class MtutManager:
    def __init__(self, mtut_file_path):
        self.path = mtut_file_path
        self.data: list = self.load_file()

    def load_file(self):
        with open(self.path, "r") as mtut_file:
            data = mtut_file.readlines()
        return data

    def save_file(self):
        with open(self.path, "w") as mtut_file:
            for line in self.data:
                mtut_file.write(line)

    def find_var_string(self, var_name: str):
        for num_line, line in enumerate(self.data):
            if line.startswith(var_name):
                return num_line
        return -1

    def get_var(self, var_name: str):
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            print(f'This variable: {var_name} does not exist in MTUT file.')
            raise ValueError
        var_line = self.data[var_index]
        var_value = self._get_var_value_from_string(var_line, var_name)
        return var_value

    def set_var(self, var_name: str, new_value: str):
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            print(f'This variable: {var_name} does not exist in MTUT file.')
            raise ValueError
        var_line = self.data[var_index]
        new_var_line = self._set_var_value_to_string(var_line, var_name, new_value)
        self.data[var_index] = new_var_line

    @staticmethod
    def _get_var_value_from_string(var_line: str, var_name: str):
        pattern = r"\s*({})\s*\n*".format(re.escape(var_name))
        return re.sub(pattern, "", var_line).rstrip('\n')

    @staticmethod
    def _set_var_value_to_string(var_line: str, var_name: str, new_value: str):
        pattern = r"\s*({})\s*".format(re.escape(var_name))
        old_value = re.sub(pattern, "", var_line).rstrip('\n')
        new_var_line = var_line.replace(old_value, new_value)
        return new_var_line


