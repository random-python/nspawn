from nspawn.support.typing import *
from dataclasses import dataclass


@dataclass(frozen=True)
class Basic():
    value:int

    @cached_method
    def making_value(self, arg1:str='arg1', arg2:str='arg2') -> int:
        print(f"making_value : {self}")
        return self.value


def test_cached_method():
    print()

    basic = Basic(101)

    print(basic.making_value())
    print(basic.making_value())
    print(basic.making_value())
