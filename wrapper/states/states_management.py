import json
import sys
from dataclasses import dataclass
from typing import Union

from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutManager, UdrmVectorManager


@dataclass
class StateStatuses:
    ERROR = -1
    SAME = 1
    CHANGED = 2
    END = 3


class State:
    def __init__(self, value: dict):
        self.value = value
        self.status: Union[int, None] = None
        self.statuses = StateStatuses

    def set_status(self, status):
        self.status = status

    def get_status(self):
        if self.status:
            return self.status
        else:
            raise ValueError('State status has not set yet.')


class StatesMachine:
    """
    Responsible for handle of automatic modes' states.
    Keep and load current state from file.
    """
    def __init__(self, config: Config):
        self.config = config
        self.mtut_manager = MtutManager(config.paths.mtut)
        # Dependencies of modes
        # Describe State
        self.state: Union[State, None] = None

    def update_state(self) -> Union[int, None]:
        """
        Update current state that is loaded from file and returns a state status code.
        Possible status codes:
        ERROR = -1
        SAME = 1
        CHANGED = 2
        END = 3
        None
        :return state_status code: state status code
        """
        # Check is at least one of modes enabled
        if any(value for value in self.config.modes.__dict__.values() if value):
            self.load_state()
            self.set_state()
            if self.state.get_status() == self.state.statuses.CHANGED:
                self.dump_state()
                return self.state.statuses.CHANGED
            elif self.state.get_status() == self.state.statuses.END:
                state_status_end = self.state.statuses.END
                self.flush_state()
                return state_status_end
            else:
                print('Impossible state.')
        else:
            print('Full manual mode enabled.')

    def load_state(self):
        """
        Loads state from file
        :return: None
        """
        state_file_path = self.config.paths.current_state
        with open(state_file_path, "r") as state_file:
            state_dict = json.load(state_file)
        self.state = State(state_dict)

    def dump_state(self):
        """
        Dumps state value to current_state.json file
        :return: None
        """
        state_file_path = self.config.paths.current_state
        with open(state_file_path, "w") as state_file:
            json.dump(self.state.value, state_file)

    def set_state(self):
        """
        Set state requirements to MTUT file if they have set in current_state.json
        and set state status code.
        :return: None
        """
        # Mode conditions should be checked here
        if self.config.modes.udrm_vector_mode:
            # Create vector object, which govern operations with UDRM vector from the file UDRM.txt
            udrm_vector = UdrmVectorManager(self.config.paths.udrm)
            try:
                udrm_list = udrm_vector.load()
            except (ValueError, FileNotFoundError):
                sys.exit()
            # Get udrm vector index from current state
            udrm_index = self.state.value['udrm_vector_index']
            udrm_max_index = udrm_vector.get_max_index()
            if udrm_index <= udrm_max_index:
                if not self.state.status:
                    print('UDRM vector mode activated.')
                self.state.set_status(self.state.statuses.CHANGED)
                new_udrm = str(udrm_list[udrm_index])
                self.mtut_manager.set_var('UDRM', new_udrm)
                # Increment vector index
                self.state.value['udrm_vector_index'] += 1
            else:
                self.state.set_status(self.state.statuses.END)

    def flush_state(self):
        """
        Set all state values in variables and file to default
        :return:
        """
        self.state.value['udrm_vector_index'] = 0
        self.dump_state()
        self.state = None
