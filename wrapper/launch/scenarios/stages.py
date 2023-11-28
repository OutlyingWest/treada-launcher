from typing import Union

from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.core.treada_io_handler import TreadaRunner
from wrapper.launch.result_builder import transient_result_build
from wrapper.launch.scenarios.scenario_builder import Stage


class Stages:
    """
    The class that allows to transmit values from stage to stage.
    """
    def __init__(self, relative_time: float):
        self.previous_stage_last_current: Union[float, None] = None
        self.relative_time = relative_time

    def without_light(self, mtut_stage_configer: MtutStageConfiger, config: Config,
                      scenario_stage: Stage):
        mtut_stage_configer.light_off(scenario_stage.mtut_vars)
        treada = TreadaRunner(config, self.relative_time)
        if config.flags.dark_result_saving:
            treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name)
            # Collect data and build result
            transient_result_build(config, scenario_stage, self.previous_stage_last_current, self.relative_time)
        else:
            treada.run(stage_name=scenario_stage.name)
        self.previous_stage_last_current = treada.get_last_step_current()

    def with_light(self, mtut_stage_configer: MtutStageConfiger, config: Config, scenario_stage: Stage):
        mtut_stage_configer.light_on(scenario_stage.mtut_vars)
        treada = TreadaRunner(config, self.relative_time)
        treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name)
        # Collect data and build result
        transient_result_build(config, scenario_stage, self.previous_stage_last_current, self.relative_time)
        self.previous_stage_last_current = treada.get_last_step_current()

    @staticmethod
    def fields_integral_calculation(scenario, config: Config):
        from wrapper.misc.collections.fields_integral.fields_integral_calculation import (
            load_mtut_vars,
            perform_fields_integral_finding,
            save_integral_results)
        mtut_vars = load_mtut_vars(config.paths.treada_core.mtut)
        results_data = perform_fields_integral_finding(scenario, config, mtut_vars)
        save_integral_results(results_data, mtut_vars)

    def capacity_third(self, config: Config, scenario_stage: Stage):
        treada = TreadaRunner(config, self.relative_time)
        treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name)

    def capacity_info_collecting(self, config: Config, scenario_stage: Stage):
        treada = TreadaRunner(config, self.relative_time)
        treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name)





