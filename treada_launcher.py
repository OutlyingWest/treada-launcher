from wrapper.io_handler import TreadaRunner
from wrapper.config.config_builder import load_config
from wrapper.data_management import MtutStageConfiger, ResultBuilder
from wrapper.ui.plotting import plot_builder


def main():
    config = load_config('config.json')
    mtut_stage_configer = MtutStageConfiger(config.paths.mtut)

    # Stage 1 - without light
    mtut_stage_configer.light_off(config.stages.light_off)
    treada = TreadaRunner(config.paths.treada_exe)
    treada.light_off()

    # Stage 2 - with light
    mtut_stage_configer.light_on(config.stages.light_on)
    treada = TreadaRunner(config.paths.treada_exe)
    treada.light_on(config.paths.treada_raw_output)

    # Save data in result file and output in console
    result_builder = ResultBuilder(mtut_file_path=config.paths.mtut,
                                   treada_raw_output_path=config.paths.treada_raw_output,
                                   result_path=config.paths.treada_result_output)
    result_builder.save_data()
    # Plot result
    plot_builder(result_builder.result_path)


if __name__ == '__main__':
    main()
