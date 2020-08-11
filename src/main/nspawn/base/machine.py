"""
Machine operations
"""

import os
import uuid
import logging
from typing import List, Mapping
from dataclasses import dataclass, replace, asdict, field

from nspawn.base.image import (
    ImageStore,
    image_store_from_url,
    perform_image_get_steps,
)
from nspawn.base.overlay import (
    ResourceOverlay,
    perform_overlay_from_image,
)
from nspawn.wrapper.base import system_command, Command
from nspawn.wrapper.sudo import SUDO
from nspawn.wrapper.systemctl import SYSTEM_CTL
from nspawn.wrapper.systemd_nspawn import SYSTEMD_NSPAWN

from nspawn import CONFIG
from nspawn.base.profile import ProfileBucket
from nspawn.base.profile import host_bind_entry_list, host_overlay_entry_list

logger = logging.getLogger(__name__)


def machine_runtime_root():
    return CONFIG['storage']['runtime']


@dataclass(frozen=True)
class MachineMeta:
    """
    Service unit file meta data
    """
    machine_name:str
    machine_template:str

    unit_conf:List[str] = field(default_factory=list)
    service_conf:List[str] = field(default_factory=list)
    install_conf:List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MachineStore:
    """
    Container runtime resources
    #
    layout example:
    runtime root:     /var/lib/nspawn/runtime
    machine base dir: /var/lib/nspawn/runtime/<machine>
    machine root dir: /var/lib/nspawn/runtime/<machine>/root
    machine work dir: /var/lib/nspawn/runtime/<machine>/work
    machine zero dir: /var/lib/nspawn/runtime/<machine>/zero
    #
    """

    # /var/lib/nspawn/runtime

    machine_name:str
    runtime_root:str = field(repr=False)

    def base_dir(self) -> str:
        return f"{self.runtime_root}/{self.machine_name}"

    def root_dir(self) -> str:
        return f"{self.base_dir()}/root"

    def work_dir(self) -> str:
        return f"{self.base_dir()}/work"

    def zero_dir(self) -> str:
        return f"{self.base_dir()}/zero"

    # /etc/systemd

    def network_file(self) -> str:
        return f"/etc/systemd/network/{self.machine_name}.network"

    def profile_file(self) -> str:
        return f"/etc/systemd/nspawn/{self.machine_name}.nspawn"

    def service_file(self) -> str:
        return f"/etc/systemd/system/{self.machine_name}.service"

    # /var/lib/machines

    def mount_point(self) -> str:
        return f"/var/lib/machines/{self.machine_name}"


def render_conf_as_list(data_dict:Mapping[str, str]) -> List[str]:
    return [
        f"{key}={value}"
        for key, value in data_dict.items()
    ]


@dataclass(frozen=True)
class MachineResult:
    """
    Container service representation used by service template
    """

    machine_meta:MachineMeta
    machine_store:MachineStore
    resource_overlay:ResourceOverlay
    profile_bucket:ProfileBucket = ProfileBucket()

    delay:float = 0.25  # TODO

    def machine_name(self) -> str:
        return self.machine_meta.machine_name

    def machine_template(self) -> str:
        return self.machine_meta.machine_template

    def machine_directory(self) -> str:
        return self.machine_store.mount_point()

    def dependency_list(self) -> List[str]:
        """
        List of extract folders resulted from all image PULL()
        """
        return self.resource_overlay.image_root_list()

    def unit_conf_list(self) -> List[str]:
        "User entries for [Unit] section"
        return self.machine_meta.unit_conf

    def service_conf_list(self) -> List[str]:
        "User entries for [Service] section"
        return self.machine_meta.service_conf

    def install_conf_list(self) -> List[str]:
        "User entries for [Install] section"
        return self.machine_meta.install_conf

    def mount_options(self) -> str:
        root_path = self.resource_overlay.render_root_path()
        zero_dir = self.machine_store.zero_dir()
        lowerdir = f"{root_path}:{zero_dir}"
        upperdir = self.machine_store.root_dir()
        workdir = self.machine_store.work_dir()
        mount_opts = CONFIG['machine']['overlayfs_mount_opts']
        return f"{mount_opts},lowerdir={lowerdir},upperdir={upperdir},workdir={workdir}"

    def mount_dir_create(self) -> Command:
        point = self.machine_store.mount_point()
        return self.folder_create(point)

    def mount_dir_delete(self) -> Command:
        point = self.machine_store.mount_point()
        return self.folder_delete(point)

    def mount_point_test(self) -> Command:
        test = system_command('mountpoint')
        point = self.machine_store.mount_point()
        return Command([test, point])

    def mount_point_create(self) -> Command:
        mount = system_command('mount')
        point = self.machine_store.mount_point()
        options = self.mount_options()
        return Command([mount, '-t', 'overlay', '-o', options, 'overlay', point])

    def mount_point_delete(self) -> Command:
        umount = system_command('umount')
        point = self.machine_store.mount_point()
        return Command([umount, point])

    def mount_point_ensure(self) -> Command:  # TODO
        shell = system_command('sh')
        test = " ".join(self.mount_point_test())
        create = " ".join(self.mount_point_create())
        return Command([shell, '-c', f"until {test} ; do {create} ; sleep {self.delay} ; done" ])

    def mount_point_desure(self) -> Command:  # TODO
        shell = system_command('sh')
        test = " ".join(self.mount_point_test())
        delete = " ".join(self.mount_point_delete())
        return Command([shell, '-c', f"while {test} ; do {delete} ; sleep {self.delay} ; done" ])

    def folder_create(self, path) -> Command:
        mkdir = system_command('mkdir')
        return Command([mkdir, '-p', path])

    def folder_delete(self, path) -> Command:
        rm = system_command('rm')
        return Command([rm, '-r', '-f', path])

    def file_create(self, path) -> Command:
        touch = system_command('touch')
        return Command([touch, '-a', path])

    def total_entry_list(self):
        entry_list = []
        entry_list.extend(self.resource_overlay.profile_entry_list())
        entry_list.extend(self.profile_bucket.entry_list)
        return entry_list

    def host_ensure_list(self) -> List[Command]:
        """
        Ensure host resources listed in systemd-nspawn Bind() and Overlay()
        """
        command_list = []
        use_bind_stub = CONFIG['machine'].getboolean('use_bind_stub')
        if use_bind_stub:
            entry_list = self.total_entry_list()
            bind_entry_list = host_bind_entry_list(entry_list)
            overlay_entry_list = host_overlay_entry_list(entry_list)
            for bind_entry in bind_entry_list:
                host_path = bind_entry.host_path()
                if bind_entry.has_folder():
                    command_list.append(self.folder_create(host_path))
                else:
                    base_path = os.path.dirname(host_path)
                    command_list.append(self.folder_create(base_path))
                    command_list.append(self.file_create(host_path))
            for overlay_entry in overlay_entry_list:
                path_list = overlay_entry.host_path_list()
                for path in path_list:
                    command_list.append(self.folder_create(path))
        return command_list

    def nspawn_exec_start(self) -> Command:
        """
        Container start command
        """
        program = SYSTEMD_NSPAWN.binary
        return Command([program])

    def nspawn_report_list(self) -> List[str]:
        """
        Container configuration report
        """
        report_list = []
        entry_list = self.total_entry_list()
        for entry in entry_list:
            origin = entry.origin
            option = entry.render_option()
            report_list.append(f"{option} :: {origin}")
        return report_list

    def nspawn_option_list(self) -> List[str]:
        """
        Container configuration settings
        """
        option_list = []
        overlay_option_list = self.resource_overlay.render_profile_option_list(quote="'")
        profile_option_list = self.profile_bucket.render_option_list(quote="'")
        if overlay_option_list:
            option_list.extend(overlay_option_list)
        if profile_option_list:
            option_list.extend(profile_option_list)
        #
        profile_command = self.profile_bucket.command
        overlay_command = self.resource_overlay.render_profile_command()
        if profile_command:
            option_list.extend(profile_command)
        elif overlay_command:
            option_list.extend(overlay_command)
        return option_list

    def nspawn_exec_stop(self) -> Command:
        """
        Container stop command
        """
        program = system_command('true')
        return Command([program])

    def resource_create_list(self) -> List[Command]:
        """
        Container resource creation commands
        """
        return [
            # ensure runtime folders
            self.folder_create(self.machine_store.base_dir()),
            self.folder_create(self.machine_store.root_dir()),
            self.folder_create(self.machine_store.work_dir()),
            self.folder_create(self.machine_store.zero_dir()),
            # ensure machine mount
            self.mount_dir_create(),
            self.mount_point_create(),
        ]

    def resource_delete_list(self) -> List[Command]:
        """
        Container resource deletion commands
        """
        return [
            # desure machine mount
            self.mount_point_delete(),
            self.mount_dir_delete(),
            # desure runtime folders
            self.folder_delete(self.machine_store.base_dir()),
        ]


def produce_service_text(machine_result:MachineResult) -> str:
    from nspawn.template.loader import machine_service
    return machine_service(machine=machine_result)


def machine_result_from_url(image_url:str, machine_meta:MachineMeta) -> MachineResult:
    image_store = image_store_from_url(image_url)
    image_store = perform_image_get_steps(image_store)
    return machine_result_from_image(image_store, machine_meta)


def machine_result_from_image(image_store:ImageStore, machine_meta:MachineMeta) -> MachineResult:
    resource_overlay = ResourceOverlay()
    perform_overlay_from_image(image_store, resource_overlay)
    machine_store = MachineStore(machine_meta.machine_name, machine_runtime_root())
    machine_result = MachineResult(machine_meta, machine_store, resource_overlay)
    return machine_result


def perform_exec_create(machine_result:MachineResult) -> None:
    "create machine runtime environment: folders and mounts"
    for command in machine_result.resource_create_list():
        SUDO.execute_unit_sert(command)


def perform_exec_delete(machine_result:MachineResult) -> None:
    "delete machine runtime environment: folders and mounts"
    for command in machine_result.resource_delete_list():
        SUDO.execute_unit_sert(command)


def perform_machine_create(machine_result:MachineResult) -> None:
    "create machine systemd service file"
    service_text = produce_service_text(machine_result)
    service_file = machine_result.machine_store.service_file()
    SUDO.file_save(service_file, service_text)
    SYSTEM_CTL.daemon_reload()


def perform_machine_delete(machine_result:MachineResult) -> None:
    "delete machine systemd service file"
    service_file = machine_result.machine_store.service_file()
    SUDO.files_delete(service_file)
    SYSTEM_CTL.daemon_reload()


def perform_machine_runtime_erase(machine_result:MachineResult) -> None:
    "remove machine runtime folder, i.e,:"
    "/var/lib/nspawn/runtime/<machine>"
    base_dir = machine_result.machine_store.base_dir()
    SUDO.files_delete(base_dir)
