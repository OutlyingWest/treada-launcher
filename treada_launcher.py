from wrapper.io_handler import TreadaRunner
from wrapper.config_builder import load_config
from wrapper.data_management import MtutStageConfiger


def main():
    config = load_config('config.json')
    mtut_stage_configer = MtutStageConfiger(config)

    # Stage 1 - without light
    # mtut_stage_configer.light_off()
    # treada = TreadaRunner(config)
    # treada.light_off()

    # Stage 2 - with light
    mtut_stage_configer.light_on()
    treada = TreadaRunner(config)
    treada.light_on()


if __name__ == '__main__':
    main()
