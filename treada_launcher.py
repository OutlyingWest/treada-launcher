from wrapper.io_handler import treada_runner
from wrapper.config_builder import load_config

treada_runner(load_config('config.json'))
