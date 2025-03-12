"""
Custom configuration parser
"""

import io
import os
import configparser
from typing import Any, List, Text, Mapping
from jinja2 import Template


def render_config_parser(config_parser: configparser.ConfigParser):
    return {section: dict(config_parser[section]) for section in config_parser.sections()}


class EnvironmentInterpolation(configparser.ExtendedInterpolation):

    def before_get(self, parser, section, option, value, defaults):
        # environment varialbes
        value = os.path.expandvars(value)
        # config file variables
        value = super().before_get(parser, section, option, value, defaults)
        return value


class RichConfigParser(configparser.ConfigParser):

    def __init__(self):
        super().__init__(self, interpolation=EnvironmentInterpolation())

    def __str__(self):
        text = io.StringIO()
        for section in self.sections():
            text.write(f"[{section}]\n")
            for (name, value) in self.items(section):
                text.write(f"{name}={value}\n")
        return text.getvalue()

    def get_list(self, section, option) -> List[Text]:
        value = self.get(section, option)
        return produce_list(value)

    def get_list_int(self, section, option) -> List[int]:
        result = self.get_list(section, option)
        result = produce_list(result)
        result = map(int, result)
        return result

    def get_template(self, section, option, context) -> Text:
        result = self.get(section, option)
        template = Template(result)
        result = template.render(context=context)
        return result

    def get_template_list(self, section, option, context) -> List[Text]:
        result = self.get_template(section, option, context)
        return produce_list(result)


def produce_list(text:Text) -> List[Text]:
        result = text.splitlines()
        result = map(Text.strip, result)
        result = filter(None, result)
        return list(result)
