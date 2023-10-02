import json
from dataclasses import dataclass
from typing import Union

from wrapper.config.config_builder import Config, load_config
from wrapper.core.data_management import MtutManager, UdrmVectorManager


@dataclass(frozen=True)
class StateStatuses:
    ERROR = -1
    CHANGED = 2
    END = 3
    MANUAL = 4


class State:
    def __init__(self, value=None):
        if value is None:
            self.value = dict()
        else:
            self.value = value
        self.status: Union[int, None] = None
        self.statuses = StateStatuses
        self.addition_info: dict

    def set_status(self, status):
        self.status = status

    def get_status(self):
        if self.status:
            return self.status
        else:
            raise ValueError('State status not set yet.')


class StatesMachine:
    """
    Responsible for handle of automatic modes' states (that influences on "Treada" runtime).
    Keep and load current state from current_state.json file.
    """
    def __init__(self):
        self.config = load_config('config.json')
        # Describe State
        self.state = State()
        self.statuses = StateStatuses

    def update_state(self) -> Union[int, None]:
        """
        Update current state that is loaded from file and returns a state status code.
        Possible status codes:
        ERROR = -1
        CHANGED = 2
        END = 3
        MANUAL = 4
        :return state_status code: state status code
        """
        # Check is at least one of modes enabled
        if any(value for value in self.config.modes.__dict__.values() if value):
            self.load_states()

            if self.config.modes.udrm_vector_mode:
                self.set_udrm_vector_state()

            return self.check_state()
        else:
            print('UDRM manual mode enabled.')
            return self.statuses.MANUAL

    def load_states(self):
        """
        Loads state from file
        :return: None
        """
        state_file_path = self.config.paths.input.state
        with open(state_file_path, "r") as state_file:
            state_dict = json.load(state_file)
        self.state = State(state_dict)

    def dump_states(self):
        """
        Dumps state value to current_state.json file
        :return: None
        """
        state_file_path = self.config.paths.input.state
        with open(state_file_path, "w") as state_file:
            json.dump(self.state.value, state_file)

    def check_state(self) -> int:
        if self.state.get_status() == self.statuses.CHANGED:
            self.dump_states()
            return self.state.statuses.CHANGED
        elif self.state.get_status() == self.statuses.END:
            state_status_end = self.statuses.END
            self.flush_state()
            return state_status_end
        else:
            print('Impossible state.')

    def set_udrm_vector_state(self):
        """
        Set UDRM to MTUT file if they have set in current_state.json
        and set state status code.
        :return: None
        """
        # Create vector object, which govern operations with UDRM vector from the file UDRM.txt
        udrm_vector = UdrmVectorManager(self.config.paths.input.udrm)
        udrm_list = udrm_vector.load()
        # Get udrm vector index from current state
        udrm_index = self.state.value['udrm_vector_index']
        udrm_max_index = udrm_vector.get_max_index()
        if udrm_index <= udrm_max_index:
            if not self.state.status:
                print('UDRM vector mode activated.')
            self.state.set_status(self.statuses.CHANGED)
            new_udrm = str(udrm_list[udrm_index])
            # Create the mtut_manager, which loads a mtut file
            mtut_manager = MtutManager(self.config.paths.treada_core.mtut)
            mtut_manager.load_file()
            # Set and save UDRM to MTUT file
            mtut_manager.set_var('UDRM', new_udrm)
            mtut_manager.save_file()
            # Increment vector index
            self.state.value['udrm_vector_index'] += 1
        else:
            self.state.set_status(self.statuses.END)

    def flush_state(self):
        """
        Set all state values in variables and file to default
        :return:
        """
        self.state.value['udrm_vector_index'] = 0
        self.dump_states()
        self.state = State()
