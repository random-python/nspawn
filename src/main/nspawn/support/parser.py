"""
Custom argument parser
"""

import re
import email
from dataclasses import dataclass
from argparse import  Action, Namespace, ArgumentParser, ArgumentTypeError
from typing import List, Mapping
from configparser import ConfigParser


def parse_unquote(line:str, quote='"') -> str:
    "remove head/tail quotes"
    if line.startswith(quote) and line.endswith(quote):
        return line[1:-1]  # remove quotes
    else:
        return line


def parse_text2bool(text:str) -> bool:
    if text.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif text.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError(f"Expecting boolean in: '{text}'")


def parse_text2dict(text:str, separator='\n') -> Mapping[str, str]:
    "convert key=value text file to dict"
    data_dict = dict()
    line_list = text.split(separator)
    for line in line_list:
        if '=' in line:
            line_term = line.split('=', 1)
            key = line_term[0].strip()
            value = line_term[1].strip()
            data_dict[key] = value
    return data_dict


def parse_dict_lower_keys(data_dict:Mapping[str, str]) -> Mapping[str, str]:
    "convert dict to use lower case keys"
    temp_dict = dict()
    for key, value in data_dict.items():
        temp_dict[key.lower()] = value
    return temp_dict


def parse_header_text(text:str) -> Mapping[str, str]:
    "convert http headers to dictionary"
    line_list = re.split('\r|\n', text)
    header_list = [ line for line in line_list if ':' in line ]
    header_text = "\r\n".join(header_list)
    parser_list = email.message_from_string(header_text)
    header_dict = { key.lower() : value for key, value in parser_list.items() }
    return header_dict


@dataclass(frozen=True)
class ParseResult:
    space:Namespace
    extra:List[str]


class StoreKeyValuePair(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        key, value = values.split('=')
        setattr(namespace, key, value)


def config_parser_entry_pattern():
    """
    Parse entry: [section]key=value
    """
    return re.compile(r'\[([^\[\]]+)\]([^=]+)=(.*)')


class StoreIntoConfigParser(Action):
    """
    Store command line options as configuraton parser options
    """

    config_parser:ConfigParser

    def __init__(self, config_parser:ConfigParser, *args, **kwargs):
        self.config_parser = config_parser
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, value_list, option_string=None):
        setattr(namespace, self.dest, value_list)
        pattern = config_parser_entry_pattern()
        for value in value_list:
            match = pattern.match(value)
            if match:
                section = match.group(1)
                config_key = match.group(2)
                config_value = match.group(3)
                if self.config_parser:
                    self.config_parser.set(section, config_key, config_value)
            else:
                raise RuntimeError(f"Invalid config entry: {value}")
