import platform
from nspawn.wrapper.sudo import SUDO
from nspawn.tool import stamp
from nspawn.base.machine import *

build_stamp = stamp.build_stamp()

epoch = "3.10"
release = f"{epoch}.3"
hardware = platform.machine()
image_url = f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz"
booter_url = f"http://dl-cdn.alpinelinux.org/alpine/v{epoch}/releases/{hardware}/alpine-minirootfs-{release}-{hardware}.tar.gz"


def test_machine_result():
    print()

    machine_name = f"a-nspawn-tester-{build_stamp}"
    machine_template = CONFIG['machine']['template']
    machine_meta = MachineMeta(machine_name, machine_template)
    machine_result = machine_result_from_url(booter_url, machine_meta)
    print(machine_result)

    machine_directory = machine_result.machine_directory()

    resource_create_list = machine_result.resource_create_list()
    resource_delete_list = machine_result.resource_delete_list()

    cmd_report = f"ls -las  {machine_directory}".split()
    cmd_ensure = f"mkdir -p {machine_directory}".split()
    cmd_desure = f"rm -rf   {machine_directory}".split()

    systemd_nspawn = system_command('systemd-nspawn')

    machine_command = [
        systemd_nspawn,
        f'--quiet',
        f'--machine={machine_name}',
        f'--directory={machine_directory}',
        f'/usr/bin/env',
    ]

    try:
        print(f"invoke: {cmd_ensure}")
        SUDO.execute_unit_sert(cmd_ensure)
        result = SUDO.execute_unit_sert(cmd_report)
        print(result.stdout)
        for command in resource_create_list:
            print(f"invoke: {command}")
            SUDO.execute_unit_sert(command)
        print(f"invoke: {cmd_report}")
        result = SUDO.execute_unit_sert(cmd_report)
        print(result.stdout)
        print(f"invoke: {machine_command}")
        result = SUDO.execute_unit_sert(machine_command)
        print(result.stdout)
    finally:
        for command in resource_delete_list:
            print(f"invoke: {command}")
            print(command)
            SUDO.execute_unit_sert(command)
        SUDO.execute_unit_sert(cmd_desure)
