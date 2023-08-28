from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.core.treada_io_handler import TreadaSwitcher
from wrapper.launch.functions import result_build


def without_light(mtut_stage_configer: MtutStageConfiger, config: Config):
    mtut_stage_configer.light_off(config.stages.light_off)
    treada = TreadaSwitcher(config)
    if config.flags.dark_result_saving:
        treada.light_off(config.paths.result.temporary.raw)
        # Collect data and build result
        result_build(config, stage_name=config.stages.names.light_off)
    else:
        treada.light_off()


def with_light(mtut_stage_configer: MtutStageConfiger, config: Config):
    mtut_stage_configer.light_on(config.stages.light_on)
    treada = TreadaSwitcher(config)
    treada.light_on(config.paths.result.temporary.raw)
    # Collect data and build result
    result_build(config, stage_name=config.stages.names.light_on)






