from nspawn.tool.stamp import build_stamp

from nspawn.wrapper.sudo import *

from nspawn.wrapper.systemd_nspawn import *


# see https://github.com/systemd/systemd/blob/master/src/nspawn/nspawn.c#L4814
def test_empty_invoke():
    print()
    machine = f"tester-{build_stamp()}"
    command = ['/usr/bin/env']

    root_dir = f"/var/lib/machines/{machine}"
    check_dir = f"{root_dir}/usr"  # expected by systemd
    SUDO.folder_ensure(check_dir)

    result = SYSTEMD_NSPAWN.execute_flow(machine, command)
    print(result)

    SUDO.files_delete(root_dir)

    assert result.rc == 1
