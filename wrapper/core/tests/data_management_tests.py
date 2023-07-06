import timeit
import unittest

import numpy as np

from wrapper.core.data_management import UdrmVectorManager, FileManager, TreadaOutputParser
from wrapper.config.config_builder import load_config


class UdrmVectorManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.udrm_vector = UdrmVectorManager(self.config.paths.input.udrm)

    def test_load(self):
        if self.config.modes.udrm_vector_mode:
            try:
                udrm_vector = self.udrm_vector.load()
            except Exception:
                self.fail()
            self.assertTrue(udrm_vector, 'UDRM vector do not loaded from file or not exists')


class FileManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.mtut = FileManager(self.config.paths.treada_core.mtut)
        self.mtut.load_file()

    def test__get_var_value_from_string(self):
        var_value = self.mtut._get_var_value_from_string(var_line='RIMPUR   3.E+12', var_name='RIMPUR')
        self.assertEqual('3.E+12', var_value)


class TreadaOutputParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.mtut = FileManager(self.config.paths.treada_core.mtut)
        self.mtut.load_file()
        self.parser = TreadaOutputParser(self.config.paths.output.raw)

    # def test_prepare_data_speed(self):
    #     prepare_data_time = timeit.repeat('parser.prepare_data()',
    #                                       setup=f"from wrapper.core.data_management import TreadaOutputParser;"
    #                                             f"parser = TreadaOutputParser(fr'{self.config.paths.output.raw}');",
    #                                       repeat=10,
    #                                       number=50)
    #     print(f'{np.mean(prepare_data_time)=}')
    #
    # def test_load_raw_file_speed(self):
    #     load_raw_file_time = timeit.repeat('parser.load_raw_file(raw_output_path)',
    #                                       setup=f"from wrapper.core.data_management import TreadaOutputParser;"
    #                                             f"parser = TreadaOutputParser(fr'{self.config.paths.output.raw}');"
    #                                             f"raw_output_path = parser.raw_output_path"
    #                                             f"",
    #                                       repeat=10,
    #                                       number=50)
    #     print(f'{np.mean(load_raw_file_time)=}')

    def test_clean_data_speed(self):
        clean_data_time = timeit.repeat('prepared_dataframe = parser.clean_data(data_list)',
                                          setup=f"from wrapper.core.data_management import TreadaOutputParser;"
                                                f"parser = TreadaOutputParser(fr'{self.config.paths.output.raw}');"
                                                f"raw_output_path = parser.raw_output_path;"
                                                f"data_list = parser.load_raw_file(raw_output_path);"
                                                f"",
                                          repeat=10,
                                          number=50)
        print(f'{np.mean(clean_data_time)=}')
        with open('clean_data_speeds.txt', 'a') as cd_file:
            cd_file.write(str(np.mean(clean_data_time)) + '\n')


if __name__ == '__main__':
    unittest.main()
