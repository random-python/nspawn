import argparse
import textwrap
from nspawn import with_merge_parser


def nsenter_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog='nspawn-enter',
        description=textwrap.dedent(
        """\
        Containers with systemd-nspawn :: machine interaction tool.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    with_merge_parser(parser)

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        "machine",
        help="Provide machine name",
    )

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument(
        "script",
        help="Optional shell script",
        nargs='?',
        default=None,
    )

    return parser
