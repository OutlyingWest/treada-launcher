import re
from wrapper.config_builder import Config, load_config


class MtutStageConfiger:
    def __init__(self):
        self.config: Config = load_config('config.json')
        self.mtut_manager = MtutManager(self.config)

    def light_off(self):
        pass

    def light_on(self):
        pass


class MtutManager:
    def __init__(self, config: Config):
        self.data: list = self.load_file(config.paths.mtut)

    @staticmethod
    def load_file(path):
        with open(path, "r") as mtut_file:
            data = mtut_file.readlines()
        return data

    def save_file(self, path):
        with open(path, "w") as mtut_file:
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
            raise ValueError(f'This variable: {var_name} does not exist in MTUT file.')
        var_line = self.data[var_index]
        var_value = self.get_var_value_from_string(var_line, var_name)
        return var_value

    def set_var(self, var_name: str, new_value: str):
        var_index = self.find_var_string(var_name)
        if var_index == -1:
            raise ValueError(f'This variable: {var_name} does not exist in MTUT file.')
        var_line = self.data[var_index]
        new_var_line = self.set_var_value_to_string(var_line, var_name, new_value)
        self.data[var_index] = new_var_line

    @staticmethod
    def get_var_value_from_string(var_line: str, var_name: str):
        pattern = r"\s*({})\s*\n*".format(re.escape(var_name))
        return re.sub(pattern, "", var_line).rstrip('\n')

    @staticmethod
    def set_var_value_to_string(var_line: str, var_name: str, new_value: str):
        pattern = r"\s*({})\s*".format(re.escape(var_name))
        old_value = re.sub(pattern, "", var_line).rstrip('\n')
        new_var_line = var_line.replace(old_value, new_value)
        return new_var_line


conf = load_config('config.json')
mtut = MtutManager(conf)
