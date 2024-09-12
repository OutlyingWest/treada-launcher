from typing import Union

from wrapper.config.config_build import Config
from wrapper.core.data_management import MtutStageConfiger
from wrapper.core.treada_io_handling import TreadaRunner
from wrapper.launch.result_build import transient_result_build, impedance_result_build
from wrapper.launch.scenarios.scenario_build import StageData


class Stage:
    """
    The class that allows to transmit values from stage to stage.
    Note: if the plots need to be showed after the ending of calculation,
          they should be returned from the scenario function
    """
    def __init__(self, relative_time: Union[float, None] = None):
        self.previous_stage_last_current: Union[float, None] = None
        self.relative_time = relative_time
        self.transient_result = {'plots': [], 'paths': []}

    def transient(self, mtut_stage_configer: MtutStageConfiger, config: Config,
                  scenario_stage_data: StageData, stage_type='light', save_result=False):
        mtut_stage_configer.set_stage_mtut_vars(scenario_stage_data.mtut_vars)
        treada = TreadaRunner(config, self.relative_time)
        if stage_type == 'light' or config.options.dark_result_saving and stage_type == 'dark' or save_result:
            treada.run(scenario_stage_data, config.paths.result.temporary.raw)
            # Collect data and build result
            plot_window, result_path = transient_result_build(config, scenario_stage_data,
                                                              self.previous_stage_last_current,
                                                              self.relative_time)
            self.transient_result['plots'].append(plot_window)
            self.transient_result['paths'].append(result_path)
        else:
            treada.run(scenario_stage_data)
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

    def impedance_info_collecting(self, config: Config, scenario_stage_data: StageData, is_repeated: bool):
        treada = TreadaRunner(config, self.relative_time)
        treada.run(scenario_stage_data, config.paths.result.temporary.raw, is_show_stage_name=False)
        impedance_result_build(config, scenario_stage_data, is_repeated)


class SmallSignalInfoStage:
    """
    Manage of information collection on info stage.
    """
    def __init__(self, relative_time: float):
        self.relative_time = relative_time

    def repeating_impedance_info_collecting(self, config: Config, scenario_stage_data: StageData):
        # while True:
        #     self.impedance_info(config, scenario_stage)
        self.impedance_info(config, scenario_stage_data)

    def impedance_info(self, config: Config, scenario_stage_data: StageData):
        treada = TreadaRunner(config, self.relative_time)
        treada.run(scenario_stage_data, config.paths.result.temporary.raw, is_show_stage_name=False)
        impedance_result_build(config, scenario_stage_data, is_repeated=False)

    def user_input(self) -> dict:
        pass

    def set_frequency_range(self, start: float, stop: float):
        pass










