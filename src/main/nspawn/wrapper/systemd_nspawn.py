"""
Wrapper for systemd-nspawn
https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
"""

from typing import List

from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo
from nspawn.support.process import Command, ExecuteResult
from nspawn.wrapper.systemctl import SYSTEM_CTL
from nspawn.base.profile import PartitionBucket, render_option_list


class SystemdNspawn(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/systemd_nspawn')
        version = SYSTEM_CTL.property_VersionNumber()
        bucket = PartitionBucket.parse_option_list(version, self.option_list)
        if bucket.has_supported():
            supported_list = render_option_list(bucket.supported_list())
            self.with_params(self.binary, supported_list)
        if bucket.has_unsupported():
            unsupported_list = render_option_list(bucket.unsupported_list())
            self.logger.warning(f"Removing unsuppoted options: {unsupported_list}")

    def machine_command(self, machine:str, command:Command) -> Command:
        return ['--machine', machine] + command

    def execute_unit(self, machine:str, command:Command) -> ExecuteResult:
        return super().execute_unit(
            command=self.machine_command(machine, command),
        )

    def execute_flow(self, machine:str, command:Command) -> ExecuteResult:
        return super().execute_flow(
            command=self.machine_command(machine, command),
        )


SYSTEMD_NSPAWN = SystemdNspawn()
