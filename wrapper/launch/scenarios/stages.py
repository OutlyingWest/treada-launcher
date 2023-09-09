from typing import Union

from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.core.treada_io_handler import TreadaRunner
from wrapper.launch.functions import result_build
from wrapper.launch.scenarios.scenario_builder import Stage


class Stages:
    """
    The class that allows to transmit values from stage to stage.
    """
    def __init__(self):
        self.previous_stage_last_current: Union[float, None] = None

    def without_light(self, mtut_stage_configer: MtutStageConfiger, config: Config,
                      scenario_stage: Stage):
        mtut_stage_configer.light_off(scenario_stage.mtut_vars)
        treada = TreadaRunner(config)
        if config.flags.dark_result_saving:
            treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name)
            # Collect data and build result
            result_build(config, scenario_stage, self.previous_stage_last_current)
        else:
            treada.run(stage_name=scenario_stage.name)
        self.previous_stage_last_current = treada.get_last_step_current()

    def with_light(self, mtut_stage_configer: MtutStageConfiger, config: Config, scenario_stage: Stage):
        mtut_stage_configer.light_on(scenario_stage.mtut_vars)
        treada = TreadaRunner(config)
        treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name.title())
        # Collect data and build result
        result_build(config, scenario_stage, self.previous_stage_last_current)
        self.previous_stage_last_current = treada.get_last_step_current()

    def fields_integral_calculation(self, config: Config):
        pass






