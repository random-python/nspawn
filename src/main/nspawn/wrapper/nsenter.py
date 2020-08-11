"""
Wrapper for nsenter
http://man7.org/linux/man-pages/man1/nsenter.1.html
"""

import os
import sys

from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo
from nspawn.wrapper.systemctl import SystemCtl


class NSEnter(Base):

    base = Sudo()

    systemctl = SystemCtl()

    def __init__(self):
        super().__init__('wrapper/nsenter')

    def execute_invoke(self, machine:str, script:str=None) -> None:
        service = f"{machine}.service"
        init_pid = self.systemctl.machine_init_pid(service)
        root_dir = f"/var/lib/machines/{machine}"
        work_dir = f"/var/lib/machines/{machine}"
        TERM = os.environ.get('TERM')
        option_list = [
            f'-t{init_pid}',
            f'-r{root_dir}',
            f'-w{work_dir}',
            '/usr/bin/env', '-i',
            f'TERM={TERM}',
            'sh'
        ]
        if script:
            option_list.extend(['-c', script])
        command = self.full_command(option_list)
        try:
            self.logger.info(f"Invoke nsenter: {command}")
            os.execlp(command[0], *command)
        except Exception as error:
            sys.exit(f"Invoke failure: {error}")


NSENTER = NSEnter()
