"""
Proxy discovery operations
"""

import os
import socket
import logging
import functools
from contextlib import closing
from dataclasses import dataclass
from typing import Mapping, Tuple, List
from urllib.parse import urlparse
from nspawn import CONFIG

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:

    entry_map:Mapping[str, str]

    def key_for(self, scheme:str) -> str:
        return f"{scheme.lower()}_proxy"

    def key_for_no(self) -> str:
        return self.key_for('no')

    def no_proxy(self) -> str:
        return self.entry_map.get(self.key_for_no(), None)

    def has_no_proxy(self) -> bool:
        return self.key_for_no() in self.entry_map

    def with_no_proxy(self, entry:str) -> None:
        self.entry_map[self.key_for_no()] = entry

    def proxy_for(self, scheme:str) -> str:
        return self.entry_map.get(self.key_for(scheme), None)

    def has_proxy_for(self, scheme:str) -> bool:
        return self.key_for(scheme) in self.entry_map

    def with_proxy_for(self, scheme:str , entry:str) -> None:
        self.entry_map[self.key_for(scheme)] = entry.lower()

    def into_entry_list(self) -> List[str]:
        return [f"{key}={value}" for key, value in self.entry_map.items()]


def verify_proxy_connect(url:str) -> bool:
    urlbean = urlparse(url)
    host = urlbean.hostname
    port = urlbean.port
    addr = (host, port)
    timeout = float(CONFIG['proxy']['socket_timeout'])
    result = False
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as channel:
            channel.settimeout(timeout)
            channel.connect(addr)
        result = True
    except:
        result = False
    logger.debug(f"verify_proxy: {addr} result: {result}")
    return result


@functools.lru_cache(maxsize=1)  # load once per session
def discover_proxy_config() -> ProxyConfig:

    proxy_config = ProxyConfig(dict())

    proxy_check_list = CONFIG.get_list('proxy', 'proxy_check_list')
    proxy_config_text = CONFIG['proxy']['proxy_config_text']

    def apply_config(entry_text: str) -> None:
        entry_list = entry_text.splitlines()
        for entry in entry_list:
            if not '=' in entry:
                continue
            entry = entry.lower().strip()
            key, value = entry.split('=', 1)
            key, value = (key.strip(), value.strip())
            if key == 'no_proxy':
                proxy_config.with_no_proxy(value)
            elif key.endswith('_proxy'):
                scheme = key.replace('_proxy', '')
                if proxy_config.has_proxy_for(scheme):
                    pass
                elif verify_proxy_connect(value):
                    proxy_config.with_proxy_for(scheme, value)
            else:
                continue

    for proxy_check in  proxy_check_list:
        if proxy_check == 'user':
            apply_config(os.popen('env').read())
        elif proxy_check == 'root':
            apply_config(os.popen('sudo env').read())
        elif proxy_check == 'config':
            apply_config(proxy_config_text)
        else:
            raise RuntimeError(f"Invalid proxy check: {proxy_check}")

    logger.debug(f"proxy_config: {proxy_config}")

    return proxy_config
