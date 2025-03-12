"""
Wrapper for systemctl
https://www.freedesktop.org/software/systemd/man/systemctl.html
"""

import re
from typing import List
from dataclasses import dataclass

from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo
from nspawn.support.process import ExecuteResult


@dataclass(frozen=True)
class ExecInfo():
    """
    Representation of systemd ExecStart=, ExecStop=, etc,
    as reported by command: 'systemctl show --property'.
    """
    path:str
    argv:str


def parse_ExecInfo(value:str) -> ExecInfo:
    if value.startswith('{') and value.endswith('}'):
        term_text = value[1:-1]
    else:
        raise RuntimeError(f"Unknown exec_info format: {value}")
    term_list = term_text.split(' ; ')
    token_list = list(map(str.strip, term_list))
    prefix_path = 'path='
    prefix_argv = 'argv[]='
    filter_path = filter(lambda token: token.startswith(prefix_path), token_list)
    filter_argv = filter(lambda token: token.startswith(prefix_argv), token_list)
    select_path = list(filter_path)
    select_argv = list(filter_argv)
    if len(select_path) == 1:
        exec_path = select_path[0].replace(prefix_path, '')
    else:
        raise RuntimeError(f"Unknown exec_info path format: {value}")
    if len(select_argv) == 1:
        exec_argv = select_argv[0].replace(prefix_argv, '')
    else:
        raise RuntimeError(f"Unknown exec_info argv format: {value}")
    return ExecInfo(exec_path, exec_argv)


class SystemCtl(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/systemctl')

    def status(self, service:str) -> ExecuteResult:
        command = ['status', service]
        return self.execute_unit(command)

    def start(self, service:str) -> ExecuteResult:
        command = ['start', service]
        return self.execute_unit(command)

    def stop(self, service:str) -> ExecuteResult:
        command = ['stop', service]
        return self.execute_unit(command)

    def enable(self, service:str) -> ExecuteResult:
        command = ['enable', service]
        return self.execute_unit(command)

    def disable(self, service:str) -> ExecuteResult:
        command = ['disable', service]
        return self.execute_unit(command)

    def daemon_reload(self) -> ExecuteResult:
        command = ['daemon-reload']
        return self.execute_unit(command)

    def list_unit_files(self, pattern) -> ExecuteResult:
        command = ['list-unit-files', '--no-legend', pattern]
        return self.execute_unit(command)

    def has_unit(self, service:str) -> bool:
        result = self.list_unit_files(service)
#         result.assert_return()
        has_stdout = result.stdout not in ('', '\n')
        return has_stdout

    def has_active(self, service:str) -> bool:
        command = ['is-active', service]
        return self.has_success(command)

    def has_failed(self, service:str) -> bool:
        command = ['is-failed', service]
        return self.has_success(command)

    def has_enabled(self, service:str) -> bool:
        command = ['is-enabled', service]
        return self.has_success(command)

    def has_machine(self, service:str) -> bool:
        prop_start = 'ExecStart'
        if self.has_property(prop_start, service):
            from nspawn.wrapper.systemd_nspawn import SYSTEMD_NSPAWN
            supervisor = SYSTEMD_NSPAWN.binary
            exec_info = self.show_exec_info(prop_start, service)
            return supervisor == exec_info.path
        else:
            return False

    def has_property(self, name:str, service:str) -> bool:
        value = self.show_property(name, service)
        return value != ''

    def show_property(self, name:str, service:str=None) -> str:
        command = ['show', '--property', name]
        if service:
            command.append(service)
        result = self.execute_unit(command)
#         result.assert_return()
        entry = result.stdout.strip()
        value = entry.replace(f"{name}=", "")
        return value

    def show_exec_info(self, name:str, service:str) -> ExecInfo:
        value = self.show_property(name, service)
        exec_info = parse_ExecInfo(value)
        return exec_info

    def property_Version(self) -> str:
        return self.show_property('Version')

    def property_VersionNumber(self) -> int:
        version = self.property_Version()
        pattern = re.compile("^([0-9]+).*$")
        matcher = pattern.search(version)
        return int(matcher.group(1))

    def property_ExecMainPID(self, service:str) -> str:
        return self.show_property('ExecMainPID', service)

    def property_ControlGroup(self, service:str) -> str:
        return self.show_property('ControlGroup', service)

    def machine_init_pid(self, service:str) -> str:
        """
        Discover systemd-nspawn init process pid
        """
        service_main_pid = self.property_ExecMainPID(service)
        service_group_root = self.property_ControlGroup(service)
        service_group_path = f"/sys/fs/cgroup/{service_group_root}"
        service_group_payload = f"{service_group_path}/payload"

        def resolve_first_proc_pid(procs_pid_list:List[str]) -> str:
            assert procs_pid_list
            assert service_main_pid not in procs_pid_list
            return procs_pid_list[0]

        def resolve_procs_pid_list(path:str) -> List[str]:
            try:
                with open(path, 'r') as file:
                    return file.read().splitlines()
            except:
                    return []

        # native, i.e. systemd inside systemd-nspawn
        native_init_procs = f"{service_group_payload}/init.scope/cgroup.procs"
        procs_pid_list = resolve_procs_pid_list(native_init_procs)
        if procs_pid_list:
            return resolve_first_proc_pid(procs_pid_list)
        # foreing, i.e. non-systemd inside systemd-nspawn
        foreing_init_procs = f"{service_group_payload}/cgroup.procs"
        procs_pid_list = resolve_procs_pid_list(foreing_init_procs)
        if procs_pid_list:
            return resolve_first_proc_pid(procs_pid_list)
        # legacy, i.e. combined parent + child process list
        legacy_init_procs = f"{service_group_path}/cgroup.procs"
        procs_pid_list = resolve_procs_pid_list(legacy_init_procs)
        procs_pid_list.remove(service_main_pid)
        if procs_pid_list:
            return resolve_first_proc_pid(procs_pid_list)
        # TODO unsupported case
        raise RuntimeError(f"Missing init proc for '{service}'")


SYSTEM_CTL = SystemCtl()

#
#
#
