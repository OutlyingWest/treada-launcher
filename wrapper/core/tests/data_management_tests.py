import unittest

from wrapper.core.data_management import UdrmVectorManager, FileManager
from wrapper.config.config_builder import load_config


class UdrmVectorManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.udrm_vector = UdrmVectorManager(self.config.paths.udrm)

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
        self.mtut = FileManager(self.config.paths.mtut)
        self.mtut.load_file()

    def test__get_var_value_from_string(self):
        var_value = self.mtut._get_var_value_from_string(var_line='RIMPUR   3.E+12', var_name='RIMPUR')
        self.assertEqual('3.E+12', var_value)


if __name__ == '__main__':
    unittest.main()
