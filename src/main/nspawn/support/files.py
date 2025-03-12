import os
import inspect
import hashlib


def make_temp_path(prefix) -> str:
    from nspawn import CONFIG
    from nspawn.tool.stamp import build_stamp
    tempdir = CONFIG['storage']['tempdir']
    temptime = build_stamp()
    temppath = f"{prefix}-{temptime}"
    return os.path.join(tempdir, temppath)


def make_file_digest(path, block=2 ** 16) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        while True:
            buffer = file.read(block)
            if not buffer:
                break
            hasher.update(buffer)
    return hasher.hexdigest()


def discover_entry_dir() -> str:
    return os.path.dirname(discover_entry_script())


def discover_entry_script() -> str:
    this_stack = inspect.stack()
    script_file = this_stack[-1].filename
    script_path = os.path.abspath(script_file)
    return script_path


def discover_project_root() -> str:
    """
    Project repository during development
    """
    src_main = '/src/main/'
    this_dir:str = os.path.dirname(os.path.abspath(__file__))
    if src_main in this_dir:
        return this_dir.split(src_main)[0]
    else:
        return None
