import os
import sys
import subprocess


def has_import():
    try:
        import nspawn
        return True
    except ImportError:
        return False


def ensure_import():
    if has_import():
        return
    try:
        command = ['git', 'rev-parse', '--show-toplevel']
        project = subprocess.check_output(command).decode('utf-8').strip()
        path_main = f"{project}/src/main"
        path_test = f"{project}/src/test"
        sys.path.insert(0, path_main)
        sys.path.insert(0, path_test)
    except Exception as error:
        sys.exit(f"Development error: {str(error)}")


ensure_import()
