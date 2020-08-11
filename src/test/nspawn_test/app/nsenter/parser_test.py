import pytest

from nspawn.app.nsenter.parser import *


def test_parser_help():
    print()
    parser = nsenter_parser()
    help_text = parser.format_help()
    print(help_text)


def test_command():
    print()
    parser = nsenter_parser()
    args = ['machine', 'ls -las "a b c"']
    space = parser.parse_args(args)
    print(space)
    assert space.machine == 'machine'
    assert space.script == 'ls -las "a b c"'
