"""
Hatcher command parser
"""

import argparse
import textwrap
from nspawn import with_merge_parser


def hatcher_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog='nspawn-hatch',
        description=textwrap.dedent(
        """\
        Containers with systemd-nspawn :: service provisioning tool.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    with_merge_parser(parser)

    commands = parser.add_subparsers(
        title='required command',
        help='Select one of:',
        required=True,
        dest='command',
    )

    command_list = commands.add_parser(
        'list',
        help='List included services',
    )

    def with_service(parser):
        parser.add_argument(
            "service",
            help='Service name',
        )

    command_ensure = commands.add_parser(
        'ensure',
        help='Provision included service',
    )
    with_service(command_ensure)

    command_desure = commands.add_parser(
        'desure',
        help='Un-Provision included service',
    )
    with_service(command_desure)

    command_update = commands.add_parser(
        'update',
        help='Re-Provision included service',
    )
    with_service(command_update)

    parser.epilog = textwrap.dedent(
        f"""\
        command usage:\n
        {command_list.format_usage()}
        {command_ensure.format_usage()}
        {command_desure.format_usage()}
        {command_update.format_usage()}
        """
    )

    return parser
