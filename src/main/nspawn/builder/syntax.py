import logging
from nspawn.base import token
from nspawn.builder.engine import ENGINE
from nspawn.support.aspect import aspect_logger

level = logging.DEBUG


@aspect_logger(level)
def IMAGE(*args, **kwargs) -> None:
    ENGINE.register_intent(token.ImageIntent(*args, **kwargs))


@aspect_logger(level)
def PULL(*args, **kwargs) -> None:
    ENGINE.register_intent(token.PullIntent(*args, **kwargs))


@aspect_logger(level)
def EXEC(*args, **kwargs) -> None:
    ENGINE.register_intent(token.ExecIntent(*args, **kwargs))


@aspect_logger(level)
def WITH(*args, **kwargs) -> None:
    ENGINE.register_intent(token.ProfileIntent(*args, **kwargs))


@aspect_logger(level)
def FETCH(*args, **kwargs) -> None:
    ENGINE.register_intent(token.FetchIntent(*args, **kwargs))


@aspect_logger(level)
def CAST(*args, **kwargs) -> None:
    ENGINE.register_intent(token.TemplateIntent(*args, **kwargs))


@aspect_logger(level)
def COPY(*args, **kwargs) -> None:
    ENGINE.register_intent(token.CopyIntent(*args, **kwargs))


@aspect_logger(level)
def RUN(*args, **kwargs) -> None:
    ENGINE.register_intent(token.RunIntent(*args, **kwargs))


@aspect_logger(level)
def SH(*args, **kwargs) -> None:
    ENGINE.register_intent(token.ShellIntent(*args, **kwargs))


@aspect_logger(level)
def PUSH(*args, **kwargs) -> None:
    ENGINE.register_intent(token.PushIntent(*args, **kwargs))

