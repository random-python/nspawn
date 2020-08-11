
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)


def render_args_text(*args, **kwargs) -> str:
    args_list = list(map(lambda x: f"'{x}'", args))
    kwargs_list = list(map(lambda kv: f"{kv[0]}='{kv[1]}'", kwargs.items()))
    total_list = args_list + kwargs_list
    total_text = ', '.join(total_list)
    return total_text


def aspect_logger(level=logging.INFO, with_args=True, with_trap=True) -> Callable:

    def decorator(function:Callable) -> Callable:

        func_id = function.__name__

        def invoker(*args, **kwargs) -> Any:
            args_text = render_args_text(*args, **kwargs) if with_args else ""
            logger.log(level, f"{func_id}({args_text})")
            try:
                return function(*args, **kwargs)
            except Exception as error:
                if with_trap:
                    logger.error(f"{func_id}() failure: {repr(error)}")
                raise error

        return invoker

    return decorator
