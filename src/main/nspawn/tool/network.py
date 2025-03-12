import re
import functools
import urllib.request
from typing import List

from nspawn import CONFIG
from nspawn.wrapper.sudo import SUDO
from nspawn.wrapper.base import system_command


@functools.lru_cache(maxsize=1)
def interface_list() -> List[str]:
    """
    Discover available host interfaces
    """
    cmd_ip = system_command('ip')
    command = f"{cmd_ip} -o addr show up primary scope global".split()
    result = SUDO.execute_unit(command)
    result.assert_return()
    line_list = result.stdout.splitlines()
    pattern = re.compile(r"^\d+[:]\s+(\S+)\s+(.+)$")
    select = lambda line: pattern.search(line).group(1)
    face_list = list(map(select, line_list))
    return face_list


@functools.lru_cache(maxsize=1)
def select_interface() -> str:
    """
    """
    face_list = interface_list()
    if face_list:
        return face_list[0]
    else:
        raise RuntimeError("Failed to select network interface")


@functools.lru_cache(maxsize=1)
def has_internet() -> bool:
    """
    Verify public internet access
    """
    if public_address():
        return True
    else:
        return False


@functools.lru_cache(maxsize=1)
def public_address() -> str:
    """
    Discover public internet address
    """
    check_timeout = float(CONFIG['network']['check_timeout'])
    check_host_list = CONFIG.get_list('network', 'check_host_list')
    try:
        for check_url in check_host_list:
            with urllib.request.urlopen(
                url=check_url, timeout=check_timeout,
            ) as response:
                return response.read().decode().strip()
        return None
    except Exception as error:
        return None


@functools.lru_cache(maxsize=1)
def private_address() -> str:
    assert False, f"TODO"


@functools.lru_cache(maxsize=1)
def has_amazon() -> bool:
    """
    Check if an instance is running on AWS EC2
    """
    if amazon_public_address():
        return True
    else:
        return False


@functools.lru_cache(maxsize=1)
def amazon_public_address() -> str:
    """
    Obtain public address when running on AWS EC2
    """
    check_url = 'http://169.254.169.254/latest/meta-data/public-ipv4'
    check_timeout = float(CONFIG['network']['check_timeout'])
    try:
        with urllib.request.urlopen(
            url=check_url, timeout=check_timeout,
        ) as response:
            return response.read().decode().strip()
    except Exception as error:
        return None
