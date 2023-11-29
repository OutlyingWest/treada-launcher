import unittest
from timeit import timeit
from dataclasses import dataclass

from wrapper.misc.global_functions import dict_to_nested_dataclass, create_dirs
from wrapper.config.config_builder import load_config


@dataclass
class Nested:
    one: int
    two: int


@dataclass
class User:
    name: str
    age: int
    is_active: bool
    nested: Nested


class DataClassesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataclass = User(name='john', age=30, is_active=True, nested=Nested(one=1, two=2))

    def test_set_to_nested_dataclass(self):
        items_dict = dict(
            name='Her',
            one=2
        )
        dict_to_nested_dataclass(self.dataclass, items_dict)
        print(self.dataclass)


class DirsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config('config.json')

    def test_timeit_create_dirs(self):
        time = timeit(lambda: create_dirs(self.config.paths, with_file=('udrm', 'mtut_dataframe')), number=1000)
        print('time:', time)

