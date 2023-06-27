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
        self.assertEqual(status, 3)

    def test_check_udrm_update_state(self):
        # Set prerequisites
        self.config.modes.udrm_vector_mode = True
        UDRM_old_value = self.states_machine.mtut_manager.get_var('UDRM')
        print(f'{UDRM_old_value=}')

        # Check
        status = self.states_machine.update_state()
        UDRM_new_value = self.states_machine.mtut_manager.get_var('UDRM')
        print(f'{UDRM_new_value=}')
        self.assertNotEqual(UDRM_old_value, UDRM_new_value)
        if status == 3:
            self.states_machine.flush_state()

if __name__ == '__main__':
    unittest.main()
