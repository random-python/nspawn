"""
Provide image server authenication and host/port remapping
"""

import enum
from dataclasses import dataclass, field
from nspawn import CONFIG
from nspawn.support.config import RichConfigParser


class AuthType(enum.Enum):
    """
    Supported authentication types
    """
    empty = 'empty'
    basic = 'basic'
    token = 'token'


@dataclass(frozen=True)
class AnyAuth:
    """
    Base authentication data
    """
    auth_type:AuthType = field(init=False)
    auth_host:str
    auth_port:str


@dataclass(frozen=True)
class EmptyAuth(AnyAuth):
    "no authentication required"
    auth_type = AuthType.empty


@dataclass(frozen=True)
class BasicAuth(AnyAuth):
    "https://en.wikipedia.org/wiki/Basic_access_authentication"
    auth_type = AuthType.basic
    username:str
    password:str


@dataclass(frozen=True)
class TokenAuth(AnyAuth):
    "https://stackoverflow.com/questions/1592534/what-is-token-based-authentication"
    auth_type = AuthType.token
    token:str


def config_section_name(host_name:str) -> str:
    "extract host config based on host name"
    return f"auth/{host_name}"


def produce_host_auth(
        host_name:str='image',
        host_port:str=None,
        config_parser:RichConfigParser=CONFIG,
    ) -> AnyAuth:
    """
    host authentication provider:
    * change host and port
    * generate account auth entry
    """

    section_name = config_section_name(host_name)

    if config_parser.has_section(section_name):
        config_section = config_parser[section_name]

        auth_type = config_section.get('type', AuthType.empty.name)
        auth_host = config_section.get('host', host_name)  # map host
        auth_port = config_section.get('port', host_port)  # map port

        if auth_type == AuthType.empty.name:
            return EmptyAuth(auth_host, auth_port)

        if auth_type == AuthType.basic.name:
            username = config_section.get('username', None)
            password = config_section.get('password', None)
            assert username, f"basic auth needs username"
            assert password, f"basic auth needs password"
            return BasicAuth(auth_host, auth_port, username, password)

        if auth_type == AuthType.token.name:
            token = config_section.get('token', None)
            assert token, f"token auth needs token"
            return TokenAuth(auth_host, auth_port, token)

        raise RuntimeError(f"invalid auth_type: {auth_type}")

    else:

        return EmptyAuth(host_name, host_port)

