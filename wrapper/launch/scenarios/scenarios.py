from wrapper.config.config_build import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.launch.scenarios.scenario_management import scenario_function
from wrapper.launch.scenarios.stages import Stages
from wrapper.launch.scenarios import scenario_build as sb
from wrapper.ui.user_interactors import create_impedance_scenario_interactor


@scenario_function(data_class=sb.DarkToLightScenario)
def dark_to_light_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stages = Stages(kwargs.get('relative_time'))
    # Stage 1 - without light
    stages.transient(mtut_stage_configer, config, scenario.stages.dark, stage_type='dark')

    # Stage 2 - with light
    stages.transient(mtut_stage_configer, config, scenario.stages.light, stage_type='light')

    # Stage 3 (additional) - fields integral calculation
    if config.flags.fields_calculation:
        stages.fields_integral_calculation(scenario, config)


@scenario_function(data_class=sb.DarkLightDarkScenario)
def dark_light_dark_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stages = Stages(kwargs.get('relative_time'))
    # Stage 1 - without light
    stages.transient(mtut_stage_configer, config, scenario.stages.dark_first, stage_type='dark')

    # Stage 2 - with light
    stages.transient(mtut_stage_configer, config, scenario.stages.light, stage_type='light')

    # Stage 3 - without light
    stages.transient(mtut_stage_configer, config, scenario.stages.dark_second, stage_type='dark')


@scenario_function(data_class=sb.TurnOnImpulseDarkScenario)
def turn_on_impulse_dark_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stages = Stages(kwargs.get('relative_time'))
    # Stage 1 - turned-off diode, without light
    stages.transient(mtut_stage_configer, config, scenario.stages.turn_off_impulse, stage_type='dark')

    # Stage 2 - turned-on diode, without light
    stages.transient(mtut_stage_configer, config, scenario.stages.turn_on_impulse, stage_type='dark')


@scenario_function(data_class=sb.CapacityScenario)
def capacity_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stages = Stages(kwargs.get('relative_time'))
    # Stage 1 - transient
    stages.transient(mtut_stage_configer, config, scenario.stages.capacity_first, save_result=True)

    # Stage 2 - transient
    stages.transient(mtut_stage_configer, config, scenario.stages.capacity_second, save_result=True)

    # Stage 3 - transient
    stages.transient(mtut_stage_configer, config, scenario.stages.capacity_third, save_result=True)

    print(f'{scenario.stages.capacity_info=} in capacity_scenario()')
    stages.impedance_info_collecting(config, scenario.stages.capacity_info)

    def run_full_scenario():
        # Stage 1 - transient
        stages.transient(mtut_stage_configer, config, scenario.stages.capacity_first, save_result=True)

        # Stage 2 - transient
        stages.transient(mtut_stage_configer, config, scenario.stages.capacity_second, save_result=True)

        # Stage 3 - transient
        stages.transient(mtut_stage_configer, config, scenario.stages.capacity_third, save_result=True)

        stages.impedance_info_collecting(config, scenario.stages.capacity_info, is_repeated=False)

    def repeat_info_collecting_stage():
        stages.impedance_info_collecting(config, scenario.stages.capacity_info, is_repeated=True)

    def exit_action():
        raise SystemExit

    user_interactor = create_impedance_scenario_interactor(actions=[
        run_full_scenario,
        repeat_info_collecting_stage,
        exit_action
    ])

    while True:
        try:
            user_interactor.ask_question(name='choose-calculation')
        except SystemExit:
            break


@scenario_function(data_class=sb.JustLightScenario)
def just_light_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stages = Stages(kwargs.get('relative_time'))

    # Stage 1 - with light
    stages.transient(mtut_stage_configer, config, scenario.stages.light, stage_type='light')
