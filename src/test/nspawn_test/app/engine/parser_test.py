
from nspawn.app.engine.parser import *


def test_setup_action():
    print()
    print(enum_name_list(SetupAction))


def test_build_parser():
    print()
    parser = build_parser()
    help = parser.format_help()
    print(help)


def test_setup_parser():
    print()
    parser = setup_parser()
    help = parser.format_help()
    print(help)
