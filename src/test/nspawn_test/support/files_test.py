from nspawn.wrapper.sudo import Sudo

from nspawn.support.files import *

def test_stack():
    print()
    stack = inspect.stack()
    for info in stack:
        print(info)

def test_make_temp_file():
    print()
    prefix = "tester"
    temp_file = make_temp_path(prefix)
    print(temp_file)


def test_make_file_digest():
    print()
    sudo = Sudo()
    text = ""
    path = "/tmp/test_make_file_digest"
    sudo.file_save(path, text)
    digest = make_file_digest(path)
    sudo.files_delete(path)
    assert digest == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_project_root():
    print()
    project_root = discover_project_root()
    print(project_root)

def test_discover_entry_script():
    print()
    entry_path = discover_entry_script()
    print(entry_path)

def test_discover_entry_dir():
    print()
    entry_path = discover_entry_dir()
    print(entry_path)
