import unittest
from dataclasses import dataclass

from wrapper.misc.global_functions import set_to_nested_dataclass


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
        set_to_nested_dataclass(self.dataclass, items_dict)
        print(self.dataclass)
