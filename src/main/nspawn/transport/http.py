"""
HTTP/HTTPS transport provider
"""

import os
import enum
import logging
from typing import Mapping
from urllib.parse import urlparse, ParseResult

from nspawn import CONFIG
from nspawn.wrapper.sudo import SUDO
from nspawn.wrapper.curl import Curl
from nspawn.support.proxy import discover_proxy_config
from nspawn.support.files import make_temp_path
from nspawn.support.parser import parse_header_text, parse_unquote
from nspawn.transport import base
from nspawn.transport.auth import produce_host_auth, AuthType

logger = logging.getLogger(__name__)


def make_netloc(host:str, port:str) -> str:
    if host and port:
        return f"{host}:{port}"
    if host:
        return f"{host}"
    raise RuntimeError(f"Invalid host:port '{host}:{port}'")


def parse_header_file(path:str) -> Mapping[str, str]:
    text = SUDO.file_load(path)
    return parse_header_text(text)


def with_auth_url(curl:Curl, remote_url:str) -> None:
    """
    inject authentication options into curl command
    """
    remote = urlparse(remote_url)
    source_host = remote.hostname
    source_port = remote.port
    host_auth = produce_host_auth(source_host)
    target_host = host_auth.auth_host
    target_port = host_auth.auth_port if host_auth.auth_port else source_port
    netloc = make_netloc(target_host, target_port)
    result = remote._replace(netloc=netloc)
    result_url = result.geturl()
    curl.with_url(result_url)
    if host_auth.auth_type == AuthType.empty:
        pass
    elif host_auth.auth_type == AuthType.basic:
        curl.with_auth_basic(host_auth.username, host_auth.password)
    elif host_auth.auth_type == AuthType.token:
        curl.with_auth_token(host_auth.token)
    else:
        raise RuntimeError(f"Invalid authtype: {host_auth.authtype}")


def with_proxy_config(curl:Curl, remote_url:str) -> None:
    """
    inject proxy configuration
    """
    use_host_proxy = CONFIG['proxy'].getboolean('use_host_proxy')
    if use_host_proxy:
        scheme = urlparse(remote_url).scheme
        proxy_config = discover_proxy_config()
        if proxy_config.has_proxy_for(scheme):
            proxy_entry = proxy_config.proxy_for(scheme)
            curl.with_proxy_entry(proxy_entry)


class ProviderHttp(base.Provider):

    def remote_head(self, remote_url:str) -> Mapping[str, str]:
        logger.debug(f"http.head.fetch: {remote_url}")
        header_path = make_temp_path("curl-head")
        SUDO.parent_ensure(header_path)
        curl = Curl()
        with_auth_url(curl, remote_url)
        with_proxy_config(curl, remote_url)
        curl.with_file_head(header_path)
        curl.execute_unit_sert()
        header_dict = parse_header_file(header_path)
        SUDO.files_delete(header_path)
        return header_dict

    def get(self, local_url:str, remote_url:str) -> None:
        "fetch remote resource and persist headers in xattr"
        logger.debug(f"http.get.fetch: {remote_url}")
        local, remote = self.parse(local_url, remote_url)
        header_path = make_temp_path("curl-head")
        source_path = make_temp_path("curl-gets")
        target_path = local.path
        SUDO.parent_ensure(header_path)
        curl = Curl()
        with_auth_url(curl, remote_url)
        with_proxy_config(curl, remote_url)
        curl.with_file_get(source_path)
        curl.with_dump_header(header_path)
        curl.execute_unit_sert()
        header_dict = parse_header_file(header_path)
        SUDO.files_delete(header_path)
        SUDO.files_move(source_path, target_path)
        # TODO attr
        SUDO.xattr_save(target_path, header_dict)

    def put(self, local_url:str, remote_url:str) -> None:
        logger.debug(f"http.put.upload: {remote_url}")
        local, remote = self.parse(local_url, remote_url)
        curl = Curl()
        with_auth_url(curl, remote_url)
        curl.with_file_put(local.path)
        curl.execute_unit_sert()
        # TODO attr
