from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.launch.scenarios import stages


def dark_to_light(mtut_stage_configer: MtutStageConfiger, config: Config):
    # Stage 1 - without light
    stages.without_light(mtut_stage_configer, config)

    # Stage 2 - with light
    stages.with_light(mtut_stage_configer, config)


def dark_light_dark(mtut_stage_configer: MtutStageConfiger, config: Config):
    # Stage 1 - without light
    stages.without_light(mtut_stage_configer, config)

    # Stage 2 - with light
    stages.with_light(mtut_stage_configer, config)

    # Stage 3 - without light
    stages.without_light(mtut_stage_configer, config)