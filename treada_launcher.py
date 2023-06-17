from wrapper.io_handler import TreadaRunner
from wrapper.config_builder import load_config
from wrapper.data_management import MtutStageConfiger


def main():
    config = load_config('wrapper/config.json')
    mtut_stage_configer = MtutStageConfiger(config.paths.mtut)

    # Stage 1 - without light
    mtut_stage_configer.light_off(config.stages.light_off)
    treada = TreadaRunner(config.paths.treada_exe)
    treada.light_off()

    # Stage 2 - with light
    mtut_stage_configer.light_on(config.stages.light_on)
    treada = TreadaRunner(config.paths.treada_exe)
    treada.light_on(config.paths.treada_raw_output)


if __name__ == '__main__':
    main()
