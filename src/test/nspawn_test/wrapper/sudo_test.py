from nspawn.wrapper.sudo import Sudo


def test_sudo():
    sudo = Sudo()
    result = sudo.execute_unit(['ls', '-las'])
#     print(result.stdout)
#     print(result.stderr)


def test_sudo_folder_check():
    sudo = Sudo()
    assert sudo.folder_check("/tmp") is True


def test_sudo_folder_assert():
    sudo = Sudo()
    sudo.folder_assert("/tmp")


def test_sudo_folder_transfer():
    sudo = Sudo()
    source = "/tmp/nspawn-tester-source"
    target = "/tmp/nspawn-tester-target"
    sudo.folder_ensure(source)
    sudo.files_sync_full(source, target)
    sudo.files_delete(source)
    sudo.files_delete(target)


def test_sudo_file_save_load():
    sudo = Sudo()
    source = "abrakadabra"
    file = "/tmp/test_sudo_file_save_load"
    sudo.file_save(file, source)
    target = sudo.file_load(file)
    sudo.files_delete(file)
    assert source == target


def test_sudo_xattr_get_set():
    sudo = Sudo()
    name = 'tester'
    source = "abra '{' kadabra '}' abra"
    file = "/var/test-sudo-xattr-get-set"
    sudo.file_save(file, source)
    sudo.xattr_set(file, name, source)
    target = sudo.xattr_get(file, name)
    sudo.files_delete(file)
    assert source == target


def test_sudo_xattr_load_save():
    sudo = Sudo()
    assert sudo.xattr_space() == 'user.nspawn.'
    assert sudo.xattr_regex() == '^user[.]nspawn[.]'
    source = dict(
        num1='1',
        num2='2.0',
        one="one ':' one ':' one",
        two="two '{'} two [']' two",
        any="hello '{'} (###) [']' kitty",
    )
    file = "/var/test-sudo-xattr-load-save"
    sudo.file_save(file, "")
    sudo.xattr_save(file, source)
    target = sudo.xattr_load(file)
    sudo.files_delete(file)
    assert source == target
