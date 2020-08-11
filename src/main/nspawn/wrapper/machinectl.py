"""
Wrapper for machinectl
https://www.freedesktop.org/software/systemd/man/machinectl.html
"""

from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo
from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class MachineDescriptor():
    MACHINE:str
    CLASS:str
    SERVICE:str
    OS:str
    VERSION:str
    ADDRESSES:str


def descriptor_from_line(line:str) -> MachineDescriptor:
    term_list = line.split()
    term_size = len(term_list)
    invalid = '<>'
    return MachineDescriptor(
        MACHINE=term_list[0] if term_size > 0 else invalid,
        CLASS=term_list[1] if term_size > 1 else invalid,
        SERVICE=term_list[2] if term_size > 2 else invalid,
        OS=term_list[3] if term_size > 3 else invalid,
        VERSION=term_list[4] if term_size > 4 else invalid,
        ADDRESSES=term_list[5] if term_size > 5 else invalid,
    )


class MachineCtl(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/machinectl')

    def status(self, machine:str):
        command = ['status', machine]
        return self.execute_unit(command)

    def start(self, machine:str):
        command = ['start', machine]
        return self.execute_unit(command)

    def stop(self, machine:str):
        command = ['stop', machine]
        return self.execute_unit(command)

    def shell(self, machine, script=['pwd']):
        script = ['shell', '--quiet', machine] + script
        return self.execute_unit(script)

    def show(self, machine:str):
        command = ['show', machine]
        return self.execute_unit(command)

    def show_property(self, machine, name):
        command = ['show', '--name', name, '--value', machine]
        return self.execute_unit(command)

    def pid_get(self, machine:str) -> str:
        result = self.show_property(machine, 'Leader')
        result.assert_return()
        return result.stdout.strip()

    def list(self) -> List[MachineDescriptor]:
        command = ['list', '--no-legend']
        result = self.execute_unit(command)
        line_list = result.stdout.splitlines()
        meta_list = list(map(descriptor_from_line, line_list))
        return meta_list

    def has_machine(self, machine:str) -> bool:
        meta_list = self.list()
        machine_list = list(map(lambda store: store.MACHINE, meta_list))
        return machine in machine_list


MACHINE_CTL = MachineCtl()
