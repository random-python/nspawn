"""
Setup global configuration
"""

import os
import sys
import logging
from argparse import ArgumentParser
from configparser import ConfigParser


def with_merge_parser(
        argent_parser:ArgumentParser,
        config_parser:ConfigParser=None,
    ) -> ArgumentParser:
    """
    Attach an action to store command argument into configuration parser
    """

    from nspawn.support.parser import StoreIntoConfigParser

    argent_parser.add_argument(
        "--config",
        help="""
        Define config.ini override tokens,
        using TOKEN format: [section]key=value,
        i.e. [logging]level=error
        """,
        metavar='TOKEN',
        nargs='*',
        action=StoreIntoConfigParser,
        config_parser=config_parser,
    )

    return argent_parser


def make_merge_parser(config_parser:ConfigParser) -> ArgumentParser:
    argent_parser = ArgumentParser()
    with_merge_parser(argent_parser, config_parser)
    return argent_parser


def ensure_environment() -> None:
    """
    Provide environment variables expected by 'config.ini'
    """
    if os.environ.get('HOME', None) is None:
        os.environ['HOME'] = '/root'


def produce_config_parser() -> ConfigParser:
    """
    Setup global configuration
    """
    try:
        ensure_environment()
        from nspawn.support.config import RichConfigParser
        #
        config_parser = RichConfigParser()
        argent_parser = make_merge_parser(config_parser)
        # start with default options
        config_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(config_dir, "config.ini")
        config_parser.read(config_path)
        # apply first-pass override
        argent_parser.parse_known_args()
        # apply external config override
        config_path_list = config_parser.get_list('config', 'path_list')
        config_parser.read(config_path_list)
        # apply second-pass override
        argent_parser.parse_known_args()
        #
        logging.basicConfig(
            level=config_parser['logging']['level'].strip().upper(),
            datefmt=config_parser['logging']['datefmt'].strip(),
            format=config_parser['logging']['format'].strip(),
        )
        return config_parser
    except Exception as error:
        sys.exit(f"Config error: {error}")


CONFIG = produce_config_parser()
