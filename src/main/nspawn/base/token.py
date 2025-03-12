"""
DSL token support
"""

import shlex
import functools
from dataclasses import dataclass , field
from typing import Any, List, Mapping, Callable, Type

from nspawn import CONFIG
from nspawn.wrapper.base import Command
from nspawn.base.profile import ProfileBucket

#
#
#


@dataclass(frozen=True)
class AnyType:
    "base type for effect classification"


@dataclass(frozen=True)
class DeclareType(AnyType):
    "represents declaration effect"


@dataclass(frozen=True)
class ExecuteType(AnyType):
    "represents execution effect"


@dataclass(frozen=True)
class ErrorType(AnyType):
    "represents operation failure effect"


@dataclass(frozen=True)
class PublishType(AnyType):
    "represents publication effect"


def has_type_declare(instance):
    return isinstance(instance, DeclareType)


def has_type_execute(instance):
    return isinstance(instance, ExecuteType)


def has_type_publish(instance):
    return isinstance(instance, PublishType)


def has_type_error(instance):
    return isinstance(instance, ErrorType)

#
#
#


@dataclass(init=False)
class AnyIntent:
    args_list: List[Any]
    args_dict: Mapping[Any, Any]

    def __init__(self, *args_list, **args_dict):
        object.__setattr__(self, 'args_list' , args_list)
        object.__setattr__(self, 'args_dict' , args_dict)

    def __setattr__(self, *args, **kwargs):
        raise AttributeError("class is immutable")


class ImageIntent(AnyIntent):
    pass


class PullIntent(AnyIntent):
    pass


class ProfileIntent(AnyIntent):
    pass


class ExecIntent(AnyIntent):
    pass


class FetchIntent(AnyIntent):
    pass


class RunIntent(AnyIntent):
    pass


class ShellIntent(AnyIntent):
    pass


class CopyIntent(AnyIntent):
    pass


class TemplateIntent(AnyIntent):
    pass


class PushIntent(AnyIntent):
    pass


class MachineIntent(AnyIntent):
    pass

#
#
#


@dataclass(frozen=True)
class AnyEffect:
    "base class for effects"


@dataclass(frozen=True)
class ImageEffect(AnyEffect, DeclareType):
    url:str

    def __str__(self):
        return f"IMAGE(url='{self.url}')"


@dataclass(frozen=True)
class PullEffect(AnyEffect, DeclareType):
    url:str

    def __str__(self):
        return f"PULL(url='{self.url}')"


@dataclass(frozen=True, init=False)
class ProfileEffect(AnyEffect, DeclareType):
    bucket_res: ProfileBucket

    def __str__(self):
        render_entry_list = ", ".join(self.bucket_res.render_entry_list(quote="'"))
        return f"WITH({render_entry_list})"

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            raise TypeError(f"Expecting entry in format: 'key=value'")
        if len(kwargs) == 0:
            raise TypeError(f"Expecting entry in format: 'key=value'")
        bucket = ProfileBucket()
        for name, value in kwargs.items():
            bucket.with_append_entry(name, value)
        object.__setattr__(self, 'bucket_res' , bucket)


@dataclass(frozen=True)
class ExecEffect(AnyEffect, DeclareType):
    command:Command

    def __str__(self):
        return f"EXEC({self.command})"

    def __post_init__(self):
        if not isinstance(self.command, list) :
            raise TypeError("Type of 'command' must be list")


@dataclass(frozen=True, init=False)
class AnyPathEffect(AnyEffect):
    source:str
    target:str

    def __str__(self):
        return f"source='{self.source}', target='{self.target}'"

    def __init__(self, path:str=None, source:str=None, target:str=None):
        error = TypeError("Either 'path' or 'source' and 'target' must be present")
        if path is None:
            if source is not None and target is not None:
                object.__setattr__(self, 'source' , source)
                object.__setattr__(self, 'target' , target)
            else:
                raise error
        else:
            if source is None and target is None:
                object.__setattr__(self, 'source' , path)
                object.__setattr__(self, 'target' , path)
            else:
                raise error
        if not isinstance(self.source, str) :
            raise TypeError("Type of 'source' must be string")
        if not isinstance(self.target, str) :
            raise TypeError("Type of 'target' must be string")


@dataclass(frozen=True, init=False)
class CopyEffect(AnyPathEffect, ExecuteType):

    def __str__(self):
        return f"COPY({super().__str__()})"


@dataclass(frozen=True, init=False)
class TemplateEffect(AnyPathEffect, ExecuteType):
    context: Mapping[str, str]

    def __str__(self):
        return f"CAST({super().__str__()}, context='{self.context}')"

    def __init__(self, path:str=None, source:str=None, target:str=None, **kwargs):
        super().__init__(path, source, target)
        object.__setattr__(self, 'context', kwargs)
        self.context.update(
            source=self.source,
            target=self.target,
        )


@dataclass(frozen=True, init=False)
class FetchEffect(AnyPathEffect, ExecuteType):
    url:str

    def __str__(self):
        return f"FETCH(url='{self.url}', {super().__str__()})"

    def __init__(self, url:str, path:str=None, source:str=None, target:str=None):
        super().__init__(path, source, target)
        object.__setattr__(self, 'url', url)


@dataclass(frozen=True)
class AnyCmdEffect(AnyEffect):
    pass


@dataclass(frozen=True)
class ShellEffect(AnyCmdEffect, ExecuteType):
    script:str

    def __str__(self):
        return f"SH(script='{self.script}')"

    def __post_init__(self):
        if not isinstance(self.script, str) :
            raise TypeError("Type of 'script' must be 'string'")


@dataclass(frozen=True)
class RunEffect(AnyCmdEffect, ExecuteType):
    command:List[str]

    def __str__(self):
        return f"RUN(command={self.command})"

    def __post_init__(self):
        if not isinstance(self.command, list) :
            raise TypeError("Type of 'command' must be 'list'")


@dataclass(frozen=True)
class PushEffect(AnyEffect, PublishType):

    def __str__(self):
        return f"PUSH()"


@dataclass(frozen=True)
class MachineEffect(AnyEffect, DeclareType):
    name:str
    template:str = field(default=CONFIG['machine']['template'])
    # [Unit] secion
    unit_conf:List[str] = field(default_factory=list)
    # [Service] secion
    service_conf:List[str] = field(default_factory=list)
    # [Install] secion
    install_conf:List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"MACHINE("
            f"name='{self.name}', "
            f"template='{self.template}',"
            f"unit={self.unit_conf},"
            f"service={self.service_conf},"
            f"install={self.install_conf},"
            f")"
        )


MappingIntentEffect = Mapping[Type[AnyIntent], Type[AnyEffect]]

MappingEffectInvoke = Mapping[Type[AnyEffect], Callable]


@dataclass(frozen=True)
class ErrorEffect(AnyEffect, ErrorType):
    intent:AnyIntent
    error:Exception


def parse_intent(intent: AnyIntent, mapper:MappingIntentEffect) -> AnyEffect:
    try:
        intent_class = type(intent)
        effect_class = mapper[intent_class]
        return effect_class(*intent.args_list, **intent.args_dict)
    except Exception as error:
        return ErrorEffect(intent, error)


def invoke_effect(effect:AnyEffect, mapper:MappingEffectInvoke) -> Any:
    effect_type = type(effect)
    invoke_func = mapper[effect_type]
    return invoke_func(effect)


@functools.lru_cache(maxsize=1)
def mapper_intent_effect() -> MappingIntentEffect:
    mapper = dict([
        (ImageIntent, ImageEffect),
        (PullIntent, PullEffect),
        (ExecIntent, ExecEffect),
        (ProfileIntent, ProfileEffect),
        (FetchIntent, FetchEffect),
        (CopyIntent, CopyEffect),
        (TemplateIntent, TemplateEffect),
        (RunIntent, RunEffect),
        (ShellIntent, ShellEffect),
        (PushIntent, PushEffect),
        (MachineIntent, MachineEffect),
    ])
    return mapper
