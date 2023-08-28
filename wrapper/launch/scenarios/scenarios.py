from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.launch.scenarios import stages
from wrapper.launch.scenarios.scenario_builder import load_scenario, DarkToLightScenario, DarkLightDarkScenario


def dark_to_light_scenario(mtut_stage_configer: MtutStageConfiger, config: Config):
    scenario = load_scenario(config.paths.scenarios, config.scenario.active_name, DarkToLightScenario)

    # Stage 1 - without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.dark)

    # Stage 2 - with light
    stages.with_light(mtut_stage_configer, config, scenario.stages.light)


def dark_light_dark_scenario(mtut_stage_configer: MtutStageConfiger, config: Config):
    scenario = load_scenario(config.paths.scenarios, config.scenario.active_name, DarkLightDarkScenario)

    # Stage 1 - without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.dark_first)

    # Stage 2 - with light
    stages.with_light(mtut_stage_configer, config, scenario.stages.light)

    # Stage 3 - without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.dark_second)
