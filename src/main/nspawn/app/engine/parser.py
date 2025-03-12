"""
Main program parser
"""

import textwrap
from argparse import  ArgumentParser, RawTextHelpFormatter
from enum import Enum, unique
from nspawn.support.typing import enum_name_list
from nspawn import with_merge_parser


def attach_engine(parser:ArgumentParser):

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        "--script",
        help="Provide script path",
        required=True,
    )


def attach_build(parser:ArgumentParser):
    pass


@unique
class SetupAction(Enum):
    update = 'update'
    ensure = 'ensure'
    desure = 'desure'
    create = 'create'
    delete = 'delete'
    enable = 'enable'
    disable = 'disable'
    start = 'start'
    stop = 'stop'
    command = 'command'
    nsenter = 'nsenter'


def attach_setup(parser:ArgumentParser):

#     required = parser.add_argument_group('required setup arguments')

    default = SetupAction.update.name

    parser.add_argument(
        "--action",
        help=textwrap.dedent(
        f"""\
        Select setup action (default={default}):
        update : perform 'desure' then 'ensure'
        desure : perform sequence: 'stop', 'disable', 'delete'
        ensure : perform sequence: 'create', 'enable', 'start'
        create : create 'machine.service' file into /etc/systemd/system, perform 'command'
        delete : delete 'machine.service' file from /etc/systemd/system
        enable : enable 'machine.service'
        disable: disalbe 'machine.service'
        start  : start 'machine.service'
        stop   : stop 'machine.service'
        command: execute run/sh commands from setup.py
        nsenter: enter 'machine.service' namespace
        """),
        choices=enum_name_list(SetupAction),
        default=default,
#         required=True,
    )


def engine_parser(prog:str) -> ArgumentParser:
    parser = ArgumentParser(
        prog=prog,
        description=textwrap.dedent(
        """\
        Containers with systemd-nspawn :: dsl script engine.
        """),
        formatter_class=RawTextHelpFormatter,
    )
    return parser


def build_parser():
    parser = engine_parser('nspawn-build')
    with_merge_parser(parser)
    attach_engine(parser)
    attach_build(parser)
    return parser


def setup_parser():
    parser = engine_parser('nspawn-setup')
    with_merge_parser(parser)
    attach_engine(parser)
    attach_setup(parser)
    return parser
