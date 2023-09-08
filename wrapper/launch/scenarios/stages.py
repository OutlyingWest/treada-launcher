from typing import Union

from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.core.treada_io_handler import TreadaRunner
from wrapper.launch.functions import result_build
from wrapper.launch.scenarios.scenario_builder import Stage


def without_light(mtut_stage_configer: MtutStageConfiger, config: Config,
                  scenario_stage: Stage):
    mtut_stage_configer.light_off(scenario_stage.mtut_vars)
    treada = TreadaRunner(config)
    if config.flags.dark_result_saving:
        treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name)
        # Collect data and build result
        result_build(config, stage=scenario_stage)
    else:
        treada.run(stage_name=scenario_stage.name)


def with_light(mtut_stage_configer: MtutStageConfiger, config: Config, scenario_stage: Stage):
    mtut_stage_configer.light_on(scenario_stage.mtut_vars)
    treada = TreadaRunner(config)
    treada.run(config.paths.result.temporary.raw, stage_name=scenario_stage.name.title())
    # Collect data and build result
    result_build(config, stage=scenario_stage)






