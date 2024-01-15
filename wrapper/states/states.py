import json
from dataclasses import dataclass, asdict, field
from typing import Callable, Union

import dacite
import pandas as pd
from colorama import Fore, Style

from wrapper.config.config_build import Config
from wrapper.core.data_management import MtutStageConfiger, MtutDataFrameManager, MtutManager


@dataclass(frozen=True)
class StateStatuses:
    NOT_READY = 'NOT READY'
    READY = 'READY'
    RUN = 'RUN'
    END = 'END'
    MANUAL = 'MANUAL'
    ERROR = 'ERROR'
    VAR_ERROR = 'MTUT VAR ERROR'
    MTUT_ERROR = 'MTUT FILE ERROR'


state_status = StateStatuses()


class BaseState:
    states_file_path: str

    def __init__(self, index: Union[int, str], status: str, mtut_vars: dict = None):
        self.index = int(index)
        self._status = status
        self.mtut_vars = mtut_vars

    def set_status(self, status, is_dump=True):

        self._status = status
        if is_dump:
            states = self.load_states(as_dicts=True)
            if self.index < len(states):
                states[self.index]['_status'] = status
            else:
                states.append(self.__dict__)

            self.dump_states(states)

    def get_status(self):
        return self._status

    @classmethod
    def load_states(cls, as_dicts=False):
        """
        Loads state from file
        :return: None
        """
        with open(cls.states_file_path, 'r') as states_file:
            states_list = json.load(states_file)
        if as_dicts:
            states = states_list
        else:
            states = [cls(*state.values()) for state in states_list]
        return states

    @classmethod
    def dump_states(cls, states: list):
        states_dump = list()
        for state in states:
            if isinstance(state, cls):
                states_dump.append(state.__dict__)
            else:
                states_dump.append(state)
        with open(cls.states_file_path, 'w') as states_file:
            json.dump(states_dump, states_file, indent=4)

    @classmethod
    def flush_states(cls):
        states = cls.load_states(as_dicts=True)
        flushed_states = [state.set_status(state_status.NOT_READY, is_dump=False) for state in states]
        cls.dump_states(flushed_states)
        return flushed_states

    def __repr__(self):
        return f'{self.__class__.__name__}(index={self.index},status={self._status})'

    status = property(fset=set_status, fget=get_status)


class BaseStatesMachine:
    def __init__(self, config: Config, state_dataclass):
        self.config = config
        self.states = list()
        self.input_df = pd.DataFrame()
        self.State = state_dataclass
        self.State.states_file_path = self.config.paths.input.states
        self.init_machine()

    def run(self, treada_launch_function: Callable[[MtutStageConfiger, Config], None], mtut_stage_configer, config):
        for state in self.states:
            if self.config.modes.mtut_dataframe:
                self.set_mtut_vars(state.index)
            if state.status == state_status.READY:
                self.states[state.index].status = state_status.RUN
                try:
                    treada_launch_function(mtut_stage_configer, config)
                    self.states[state.index].status = state_status.END
                except Exception as e:
                    self.states[state.index].status = state_status.ERROR
                    print(f'State with index={state.index} raise an Exception: {e}')
                    input()
                    raise e

    def init_machine(self):
        if self.config.modes.mtut_dataframe:
            input_df_manager = MtutDataFrameManager(self.config.paths.input.mtut_dataframe)
            self.input_df = input_df_manager.get()
            print(f'You run "treada_launcher" in mtut_dataframe mode. MTUT vars to iterate below:')
            print(f'{self.input_df}')
            print(f'To continue and run iterations push the {Fore.GREEN}Enter{Style.RESET_ALL} button.')
            input()
            for ind, input_line in self.input_df.iterrows():
                mtut_vars = {var_name: var_value for var_name, var_value in input_line.items() if var_value}
                self.states.append(self.State(index=ind,
                                              status=state_status.NOT_READY,
                                              mtut_vars=mtut_vars))
        else:
            self.states = [self.State(0, state_status.READY)]
        self.State.dump_states(self.states)

    def set_mtut_vars(self, state_index: int):
        try:
            # Create the mtut_manager, which loads a mtut file
            mtut_manager = MtutManager(self.config.paths.treada_core.mtut)
            mtut_manager.load_file()
            # Set and save UDRM to MTUT file
            vars_seria = self.input_df.iloc[state_index]
            for var_key, var_value in vars_seria.items():
                mtut_manager.set_var(var_key, var_value)
                self.states[state_index].mtut_vars[var_key] = var_value
            mtut_manager.save_file()
            self.states[state_index].status = state_status.READY
        except ValueError:
            self.states[state_index].status = state_status.VAR_ERROR
        except FileNotFoundError:
            self.states[state_index].status = state_status.MTUT_ERROR

    def flush_states(self):
        self.states = self.State.flush_states()

