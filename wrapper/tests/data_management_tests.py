import unittest

from wrapper.data_management import UdrmVectorManager
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


if __name__ == '__main__':
    unittest.main()
