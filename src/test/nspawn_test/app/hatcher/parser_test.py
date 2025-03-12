import re
import pytest

from nspawn import CONFIG
from nspawn.app.hatcher.parser import *


def test_parser_help():
    print()
    parser = hatcher_parser()
    help_text = parser.format_help()
    print(help_text)


def test_empty_args():
    print()
    parser = hatcher_parser()
    args = []
    with pytest.raises(BaseException) as trap_info:
        parser.parse_args(args)
    assert trap_info.type == SystemExit


def test_command_list():
    print()
    parser = hatcher_parser()
    args = ['list']
    space = parser.parse_args(args)
    print(space)
    assert space.command == 'list'
    assert not hasattr(space, 'service')


def test_command_ensure():
    print()
    parser = hatcher_parser()
    args = ['ensure', 'machine']
    space = parser.parse_args(args)
    print(space)
    assert space.command == 'ensure'
    assert space.service == 'machine'


def test_command_desure():
    print()
    parser = hatcher_parser()
    args = ['desure', 'machine']
    space = parser.parse_args(args)
    print(space)
    assert space.command == 'desure'
    assert space.service == 'machine'


def test_command_update():
    print()
    parser = hatcher_parser()
    args = ['update', 'machine']
    space = parser.parse_args(args)
    print(space)
    assert space.command == 'update'
    assert space.service == 'machine'


# def test_sync_regex():
#     print()
#     service_sync_regex = CONFIG['hatcher/image-syncer']['service_sync_regex']
#     matcher = re.compile(service_sync_regex)
#     assert matcher.match("index.html")
#     assert not matcher.match("index.html.test")
#     assert matcher.match("base/arch/package.tar.gz")
#     assert not matcher.match("base/arch/package.tar.gz.test")
