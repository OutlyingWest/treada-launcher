from dataclasses import dataclass
from typing import Callable

import pandas as pd

from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger


@dataclass(frozen=True)
class StateStatuses:
    NOT_PREPARED = 1
    READY = 2
    RUN = 3
    END = 0
    ERROR = -1
    MANUAL = 4


status = StateStatuses()


class BaseState:
    def __init__(self, ):
        self.index: int
        self.status = status.NOT_PREPARED


class BaseStateMachine:
    def __init__(self, ):
        self.states = list()
        self.input_df = pd.DataFrame()

    def run(self, treada_launch_function: Callable[[MtutStageConfiger, Config], None], mtut_stage_configer, config):
        pass

    def init_states(self):
        pass

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
        pass

