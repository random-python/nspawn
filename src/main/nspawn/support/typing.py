"""
Common class traits
"""

import logging
import functools
from enum import Enum
from typing import Type, List
from nspawn.support.process import make_solo_line


def type_name(instance:object) -> str:
    """
    Object class name
    """
    return type(instance).__name__


def enum_name_list(enum_klaz:Type[Enum]) -> List[str]:
    """
    List of enumeration member names
    """
    return list(enum_klaz.__members__.keys())


class WithTypeNameTrait:
    """
    Trait: extract class name
    """

    def type_name(self) -> str:
        return type_name(self)


class WithTypeLoggerTrait:
    """
    Trait: provide logger with class based name
    """

    logger:logging.Logger

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

    def react_stdout(self, line:str) -> None:
        line = make_solo_line(line)
        self.logger.info(f"[stdout] {line}")

    def react_stderr (self, line:str) -> None:
        line = make_solo_line(line)
        self.logger.info(f"[stderr] {line}")


class cached_method:
    """
    Decorator: class method with result cache
    """

    CACHE = "__cached_method__"

    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)

    def __get__(self, instance, cls=None):
        if instance is None:
            return self.function
        return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        instance = args[0]

        if not hasattr(instance, self.CACHE):
            object.__setattr__(instance, self.CACHE, dict())

        cache = getattr(instance, self.CACHE)

        key = (self.function, frozenset(args[1:]), frozenset(kwargs.items()))

        if not key in cache:
            cache[key] = self.function(*args, **kwargs)

        value = cache[key]

        return value
