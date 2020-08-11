"""
"""

import os
from jinja2 import Template, Environment, FileSystemLoader
from nspawn.base.machine import MachineResult


def this_dir():
    return os.path.dirname(os.path.abspath(__file__))


def this_enviro() -> Environment:
    return Environment(loader=FileSystemLoader(this_dir()), trim_blocks=True)


def this_template(path:str) -> Template:
    return this_enviro().get_template(path)


def file_template(path:str) -> Template:
    with open(path) as file:
        text = file.read()
        return Template(text, trim_blocks=True)


def machine_service(machine:MachineResult) -> str:
    path = machine.machine_template()
    if os.path.isabs(path):
        template = file_template(path)
    else:
        template = this_template(path)
    text = template.render(machine=machine)
    return text
