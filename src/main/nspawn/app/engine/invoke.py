"""
Invoke engine proper when started via engine script
"""

import os
import sys
import logging

from nspawn.support.files import discover_entry_script
from nspawn.support.files import discover_project_root

logger = logging.getLogger(__name__)

this_dir:str = os.path.dirname(os.path.abspath(__file__))


def env_get(name: str) -> str:
    return os.environ.get(name, None)


def env_set(name: str, value: str) -> None:
    os.environ[name] = value


class InvokeState():
    """
    Maintain engine invocation state
    """

    invoke_key = "NSPAWN_ENGINE_INVOKE"

    @staticmethod
    def invoke_get() -> str:
        return env_get(InvokeState.invoke_key)

    @staticmethod
    def invoke_set(invoke_value: str="true") -> None:
        env_set(InvokeState.invoke_key, invoke_value)


class PythonPath():
    """
    Inject project repository during development
    """

    python_key = 'PYTHONPATH'

    @staticmethod
    def value() -> str:
        return env_get(PythonPath.python_key)

    @staticmethod
    def ensure_project() -> None:
        project_root = discover_project_root()
        if project_root:
            PythonPath.inject_project(project_root)

    @staticmethod
    def inject_project(project_root:str) -> None:
        path_main = f"{project_root}/src/main"
        path_test = f"{project_root}/src/test"
        module_path = f"{path_main}:{path_test}"
        python_path = env_get(PythonPath.python_key)
        if python_path:
            python_path = f"{module_path}:{python_path}"
        else:
            python_path = f"{module_path}"
        env_set(PythonPath.python_key, python_path)
        logger.debug(f"Python path: {python_path}")


def invoke_main(file_name: str) -> None:
    "invoke engine proper when started via engine script"
    if InvokeState.invoke_get():
        # running inside the engine
        return
    else:
        InvokeState.invoke_set()
        PythonPath.ensure_project()
    try:
        main_file = f"{this_dir}/{file_name}"
        script_file = discover_entry_script()
        command = [
            sys.executable,
            main_file,
            '--script',
            script_file,
        ] + sys.argv[1:]
        logger.info(f"Invoke engine: {command}")
        os.execlp(sys.executable, *command)
    except Exception as error:
        sys.exit(f"Invoke failure: {error}")
