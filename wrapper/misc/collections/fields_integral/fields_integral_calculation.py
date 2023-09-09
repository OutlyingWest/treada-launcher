import json
import os
from dataclasses import dataclass
from typing import List, Dict

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from wrapper.core.data_management import MtutManager
from wrapper.config.config_builder import load_config, Config
from wrapper.launch.scenarios.scenario_builder import TurnOnImpulseDarkScenario, DarkToLightScenario, load_scenario
from wrapper.misc.collections.ww_data_collecting.collect_ww_data import load_ww_data
from wrapper.misc.collections.ww_data_collecting.extract_ww_data import extract_ww_data


@dataclass
class MtutVars:
    hx:  List[Dict[str, float]]
    e_mobility: float
    h_mobility: float
    udrm: str
    # layer_material_number_1: List[float]
    # layer_material_number_2: List[float]


def load_mtut_vars(mtut_file_path: str) -> MtutVars:
    mtut_manager = MtutManager(mtut_file_path)
    mtut_manager.load_file()
    hx = mtut_manager.get_hx_var()
    e_mobility, h_mobility = mtut_manager.get_list_var('CMOB2IL', values_type=float)
    udrm = mtut_manager.get_var('UDRM')
    # layer_material_number_1 = mtut_manager.get_list_var('N1ILUM', values_type=float)
    # layer_material_number_2 = mtut_manager.get_list_var('N2ILUM', values_type=float)
    # print(f'{layer_material_number_1=}')
    # print(f'{layer_material_number_2=}')
    return MtutVars(
        hx=hx,
        e_mobility=e_mobility,
        h_mobility=h_mobility,
        udrm=udrm,
        # layer_material_number_1=layer_material_number_1,
        # layer_material_number_2=layer_material_number_2,
    )


def is_ww_data_exists(stage_folder_path: str):
    index_path = next(iter(os.listdir(stage_folder_path)))
    ww_path = os.path.join(stage_folder_path, index_path)
    file_names = os.listdir(ww_path)
    for file_name in file_names:
        if file_name.startswith('WW'):
            return True
    return False


def extract_stages_ww_data(distributions_path: str):
    for stage_folder_path in os.listdir(distributions_path):
        stage_folder_path = os.path.join(distributions_path, stage_folder_path)
        if not is_ww_data_exists(stage_folder_path):
            extract_ww_data(stage_folder_path)


def load_fields_data(distributions_path: str, scenario) -> dict:
    fields_ind = 6
    fields_alias = {fields_ind: 'fields'}
    fields_dict = dict()

    for stage in scenario.stages.__dict__.values():
        stage_name = stage.name
        stage_data_path = os.path.join(distributions_path, stage_name)
        stage_data_indexes: list = sorted(os.listdir(stage_data_path), key=int)
        # data_indexes_show = [light_data_indexes[ind] for ind in list(range(0, len(light_data_indexes), 3))]
        data_indexes_show = stage_data_indexes[-1:]
        print(f'{stage_data_indexes=}')

        fields_dict[stage_name] = load_ww_data(abs_res_path=distributions_path,
                                               stage_dir_name=stage_name,
                                               ww_dir_indexes=data_indexes_show,
                                               ww_aliases=fields_alias)
    return fields_dict


def find_between_peaks_field_range(field: pd.Series, height: float) -> np.array:
    field_peaks, _ = find_peaks(field, height=height)
    if len(field_peaks) > 2:
        raise ValueError('Field peaks number > 2')
    field_peaks[-1] += 1
    return field_peaks


def field_integral_calculation(field: pd.Series, dx: pd.Series, q_mobility: float) -> float:
    """
    :param field: Electrical field seria in kV/cm
    :param dx: step from MTUT in cm
    :param q_mobility: Electron or holes mobility
    :return: full time calculated for field range
    """
    time_seria: pd.Series = (dx / (q_mobility * field * 1e3)) * 1e12

    # pd.set_option('display.max_rows', None)
    # print(pd.DataFrame({'field': field, 'time': time_seria}))

    full_time = time_seria.sum()
    return full_time


def find_fields_integral(fields_seria: pd.Series, dx_const: float, q_mobility: float) -> float:
    low_field_ind, high_field_ind = find_between_peaks_field_range(fields_seria, height=1)
    # print(f'{low_field_ind=}, {high_field_ind=}')
    stripped_fields_seria = fields_seria.iloc[low_field_ind:high_field_ind]
    dx = pd.Series(dx_const, index=stripped_fields_seria.index)  # cm
    time = field_integral_calculation(stripped_fields_seria, dx, q_mobility)
    return time


def save_integral_results(results: dict, mtut_vars: MtutVars):
    script_path = os.path.dirname((os.path.abspath(__file__)))
    res_file_path = os.path.join(script_path, 'results', f'res_u({mtut_vars.udrm}).json')
    with open(res_file_path, 'w') as fields_result_file:
        json.dump(results, fields_result_file, indent=4)


def perform_fields_integral_finding(scenario, config: Config, mtut_vars: MtutVars):
    extract_stages_ww_data(distributions_path=config.paths.result.temporary.distributions)
    fields_data = load_fields_data(distributions_path=config.paths.result.temporary.distributions, scenario=scenario)
    print(fields_data)

    dx_const = mtut_vars.hx[1]['step'] * 1e-4  # cm

    print(f'dx = {dx_const:.4} cm')
    print(f'e, h mobilities:')
    print(f'{mtut_vars.e_mobility}, {mtut_vars.h_mobility}')
    print()

    results = {
        "e_mobility": mtut_vars.e_mobility,
        "h_mobility": mtut_vars.h_mobility,
    }
    for stage in scenario.stages.__dict__.values():
        print(f'stage: {stage.name}')

        fields_df: pd.DataFrame = next(iter(fields_data[stage.name].values()))[6]
        e_time = find_fields_integral(fields_seria=fields_df['fields'],
                                      dx_const=dx_const,
                                      q_mobility=mtut_vars.e_mobility)
        print(f'{e_time = :.4}')

        h_time = find_fields_integral(fields_seria=fields_df['fields'],
                                      dx_const=dx_const,
                                      q_mobility=mtut_vars.h_mobility)
        print(f'{h_time = :.4}')
        print()
        results[stage.name] = {
            'e_time': e_time,
            'h_time': h_time,
        }
    return results


def main():
    config = load_config('config.json')
    # Load active scenario data
    scenario = load_scenario(config.paths.scenarios, config.scenario.active_name, DarkToLightScenario)

    mtut_vars = load_mtut_vars(config.paths.treada_core.mtut)

    perform_fields_integral_finding(scenario, config, mtut_vars)
    # plt.plot(fields_df['x'], fields_df['fields'])
    # # plt.yscale('log', base=10)
    # plt.grid(True)
    # plt.show()


if __name__ == '__main__':
    main()
