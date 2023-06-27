import unittest

from wrapper.config.config_builder import load_config
from wrapper.states.states_management import StatesMachine
from wrapper.core.data_management import MtutManager


class StatesMachineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')
        self.states_machine = StatesMachine(self.config)
        self.mtut_manager = MtutManager(self.config.paths.mtut)

    def test_vector_mode_enabled_update_state(self):
        # Set prerequisites
        self.config.modes.udrm_vector_mode = True

        # Check
        status = self.states_machine.update_state()
        self.assertEqual(status, self.states_machine.state.statuses.CHANGED)

        status = self.states_machine.update_state()
        self.assertEqual(status, 3)

    def test_vector_mode_disabled_update_state(self):
        # Set prerequisites
        self.config.modes.udrm_vector_mode = False

        # Check
        status = self.states_machine.update_state()
        self.assertEqual(status, None)


if __name__ == '__main__':
    unittest.main()
