import argparse

from nspawn.support.parser import *
from nspawn.support.config import render_config_parser
from nspawn import with_merge_parser


def test_key_value():
    print()

    parser = argparse.ArgumentParser()

    parser.add_argument("action", action=StoreKeyValuePair)
    parser.add_argument("invoke", action=StoreKeyValuePair)
    parser.add_argument("script", action=StoreKeyValuePair)

    argument_list = [
        "action=build",
        "invoke=command",
        "script=some_path",
    ]
    result = parser.parse_args(argument_list)
    print(result)

    argument_list = [
        "script=some_path",
        "invoke=command",
        "action=build",
    ]
    result = parser.parse_args(argument_list)
    print(result)


def test_key_value_choices():
    print()

    parser = argparse.ArgumentParser()

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        "action",
        help="Select action",
        action=StoreKeyValuePair,
    )

    args_list = [
        "action=build",
    ]
    result = parser.parse_args(args_list)
    print(result)

    help = parser.format_help()
    print(help)


def test_entry_pattern():
    print()
    pattern = config_parser_entry_pattern()
    result = pattern.match("[section name]key name=value = entry")
    print(result)
    assert result
    assert result.group(1) == 'section name'
    assert result.group(2) == 'key name'
    assert result.group(3) == 'value = entry'


def test_store_into_config_parser():
    print()

    argent_parser = argparse.ArgumentParser()
    config_parser = ConfigParser()
    config_parser.add_section('logging')
    config_parser.add_section('machine')

    with_merge_parser(argent_parser, config_parser)

    args_list = [
        "--config=[logging]level=info",
        "--config=[logging]namer=hello-kitty",
        "--config=[machine]template=machine1.service",
        "--config", "[logging]level=debug",
        "--config", "[machine]template=machine.service",
        "--config", "[logging]level=warning", "[machine]template=machine2.service",
    ]
    result = argent_parser.parse_args(args_list)
    print(result)
    render_config = render_config_parser(config_parser)
    print(render_config)

    assert config_parser['logging']['level'] == 'warning'
    assert config_parser['logging']['namer'] == 'hello-kitty'
    assert config_parser['machine']['template'] == 'machine2.service'

    help = argent_parser.format_help()
    print(help)

