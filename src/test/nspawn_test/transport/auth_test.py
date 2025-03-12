
from nspawn.transport.auth import *

from nspawn.support.config import RichConfigParser


def test_produce_auth_image():
    print()
    host_auth = produce_host_auth('image')
    print(host_auth)
    assert host_auth.auth_type == AuthType.basic
    assert host_auth.auth_host == 'nspawn-image-server'
    assert host_auth.username == 'default'
    assert host_auth.password == 'default'


def test_produce_auth_missing():
    print()
    config_parser = RichConfigParser()
    host_auth = produce_host_auth('missing', None, config_parser)
    print(host_auth)
    assert host_auth.auth_type == AuthType.empty
    assert host_auth.auth_host == 'missing'


def test_produce_auth_empty():
    print()
    config_parser = RichConfigParser()
    config_parser.add_section('auth/empty-host')
    config_parser.set('auth/empty-host', 'type', 'empty')
    config_parser.set('auth/empty-host', 'host', 'some-empty')
    host_auth = produce_host_auth('empty-host', None, config_parser)
    print(host_auth)
    assert host_auth.auth_type == AuthType.empty
    assert host_auth.auth_host == 'some-empty'


def test_produce_auth_basic():
    print()
    config_parser = RichConfigParser()
    config_parser.add_section('auth/basic-host')
    config_parser.set('auth/basic-host', 'type', 'basic')
    config_parser.set('auth/basic-host', 'host', 'some-basic')
    config_parser.set('auth/basic-host', 'port', '1234')
    config_parser.set('auth/basic-host', 'username', 'basic-user')
    config_parser.set('auth/basic-host', 'password', 'basic-pass')
    host_auth = produce_host_auth('basic-host', None, config_parser)
    print(host_auth)
    assert host_auth.auth_type == AuthType.basic
    assert host_auth.auth_host == 'some-basic'
    assert host_auth.auth_port == '1234'
    assert host_auth.username == 'basic-user'
    assert host_auth.password == 'basic-pass'


def test_produce_auth_token():
    print()
    config_parser = RichConfigParser()
    config_parser.add_section('auth/token-host')
    config_parser.set('auth/token-host', 'type', 'token')
    config_parser.set('auth/token-host', 'host', 'some-token')
    config_parser.set('auth/token-host', 'port', '3456')
    config_parser.set('auth/token-host', 'token', 'basic-token')
    host_auth = produce_host_auth('token-host', None, config_parser)
    print(host_auth)
    assert host_auth.auth_type == AuthType.token
    assert host_auth.auth_host == 'some-token'
    assert host_auth.auth_port == '3456'
    assert host_auth.token == 'basic-token'
