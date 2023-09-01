from wrapper.config.config_builder import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.launch.functions import scenario_function
from wrapper.launch.scenarios import stages
from wrapper.launch.scenarios import scenario_builder as sb


@scenario_function(data_class=sb.DarkToLightScenario)
def dark_to_light_scenario(scenario, mtut_stage_configer: MtutStageConfiger, config: Config):
    # Stage 1 - without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.dark)

    # Stage 2 - with light
    stages.with_light(mtut_stage_configer, config, scenario.stages.light)


@scenario_function(data_class=sb.DarkLightDarkScenario)
def dark_light_dark_scenario(scenario, mtut_stage_configer: MtutStageConfiger, config: Config):
    # Stage 1 - without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.dark_first)

    # Stage 2 - with light
    stages.with_light(mtut_stage_configer, config, scenario.stages.light)

    # Stage 3 - without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.dark_second)


@scenario_function(data_class=sb.TurnOnImpulseDarkScenario)
def turn_on_impulse_dark_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger):
    # Stage 1 - turned-off diode, without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.turn_off_impulse)

    # Stage 2 - turned-on diode, without light
    stages.without_light(mtut_stage_configer, config, scenario.stages.turn_on_impulse)

