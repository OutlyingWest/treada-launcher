from wrapper.config.config_build import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.launch.scenarios.scenario_management import scenario_function
from wrapper.launch.scenarios.stages import Stage
from wrapper.launch.scenarios import scenario_build as sb
from wrapper.ui.user_interactors import create_impedance_scenario_interactor


@scenario_function(data_class=sb.DarkToLightScenario)
def dark_to_light_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stage = Stage(kwargs.get('relative_time'))
    # StageData 1 - without light
    stage.transient(mtut_stage_configer, config, scenario.stages.dark, stage_type='dark')

    # StageData 2 - with light
    stage.transient(mtut_stage_configer, config, scenario.stages.light, stage_type='light')

    # StageData 3 (additional) - fields integral calculation
    if config.flags.fields_calculation:
        stage.fields_integral_calculation(scenario, config)


@scenario_function(data_class=sb.DarkLightDarkScenario)
def dark_light_dark_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stage = Stage(kwargs.get('relative_time'))
    # StageData 1 - without light
    stage.transient(mtut_stage_configer, config, scenario.stages.dark_first, stage_type='dark')

    # StageData 2 - with light
    stage.transient(mtut_stage_configer, config, scenario.stages.light, stage_type='light')

    # StageData 3 - without light
    stage.transient(mtut_stage_configer, config, scenario.stages.dark_second, stage_type='dark')
    return stage.plots


@scenario_function(data_class=sb.TurnOnImpulseDarkScenario)
def turn_on_impulse_dark_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stage = Stage(kwargs.get('relative_time'))
    # StageData 1 - turned-off diode, without light
    stage.transient(mtut_stage_configer, config, scenario.stages.turn_off_impulse, stage_type='dark')

    # StageData 2 - turned-on diode, without light
    stage.transient(mtut_stage_configer, config, scenario.stages.turn_on_impulse, stage_type='dark')
    return stage.plots


@scenario_function(data_class=sb.CapacityScenario)
def capacity_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs):
    stage = Stage(kwargs.get('relative_time'))
    # StageData 1 - transient
    stage.transient(mtut_stage_configer, config, scenario.stages.capacity_first, save_result=True)

    # StageData 2 - transient
    stage.transient(mtut_stage_configer, config, scenario.stages.capacity_second, save_result=True)

    # StageData 3 - transient
    stage.transient(mtut_stage_configer, config, scenario.stages.capacity_third, save_result=True)

    print(f'{scenario.stages.capacity_info=} in capacity_scenario()')
    stage.impedance_info_collecting(config, scenario.stages.capacity_info, is_repeated=False)

    def run_full_scenario():
        # StageData 1 - transient
        stage.transient(mtut_stage_configer, config, scenario.stages.capacity_first, save_result=True)

        # StageData 2 - transient
        stage.transient(mtut_stage_configer, config, scenario.stages.capacity_second, save_result=True)

        # StageData 3 - transient
        stage.transient(mtut_stage_configer, config, scenario.stages.capacity_third, save_result=True)

        stage.impedance_info_collecting(config, scenario.stages.capacity_info, is_repeated=False)

    def repeat_info_collecting_stage():
        stage.impedance_info_collecting(config, scenario.stages.capacity_info, is_repeated=True)

    def exit_action():
        raise SystemExit

    user_interactor = create_impedance_scenario_interactor(actions=[
        (run_full_scenario, ),
        (repeat_info_collecting_stage, ),
        (exit_action, ),
    ])

    while True:
        try:
            user_interactor.ask_question(name='choose-calculation')
        except SystemExit:
            break


@scenario_function(data_class=sb.JustLightScenario)
def just_light_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger, **kwargs) -> list:
    stage = Stage(kwargs.get('relative_time'))

    # StageData 1 - with light
    stage.transient(mtut_stage_configer, config, scenario.stages.light, stage_type='light')
    return stage.plots


@scenario_function(data_class=sb.JustLightWithCorrectionScenario)
def just_light_with_correction_scenario(scenario, config: Config, mtut_stage_configer: MtutStageConfiger,
                                        **kwargs) -> list:
    stage = Stage(kwargs.get('relative_time'))

    # StageData 1 - with light
    stage.transient(mtut_stage_configer, config, scenario.stages.light, save_result=False)
    # StageData 2 - with light
    stage.transient(mtut_stage_configer, config, scenario.stages.light_correction, stage_type='light')
    return stage.plots
