"""
Base type for transport provider.
"""

import abc
import logging
from typing import Any, Mapping
from urllib.parse import urlparse
from nspawn.wrapper.sudo import SUDO
from nspawn.support.header import compare_header, HeadComp, discover_header

logger = logging.getLogger(__name__)


class TransportError(Exception):
    ""


class Provider(abc.ABC):
    """
    Base type for transport provider.
    """

    def parse(self, local_url:str, remote_url:str):
        local = urlparse(local_url)
        remote = urlparse(remote_url)
        return (local, remote)

    def local_head(self, local_url:str) -> Mapping[str, str]:
        "obtain meta description of local resource"
        return discover_header(local_url)

    @abc.abstractmethod
    def remote_head(self, remote_url:str) -> Mapping[str, str]:
        "obtain meta description of remote resource"

    @abc.abstractmethod
    def get(self, local_url:str, remote_url:str) -> None:
        "fetch remote resource"

    @abc.abstractmethod
    def put(self, local_url:str, remote_url:str) -> None:
        "upload local resource"

    def smart_get(self, local_url:str, remote_url:str) -> None:
        "fetch resource when local-vs-remote headers have changed"
        local, remote = self.parse(local_url, remote_url)
        if SUDO.file_check(local.path):
            logger.debug(f"smart.get.present: {remote_url}")
            local_head = self.local_head(local_url)
            remote_head = self.remote_head(remote_url)
            head_comp = compare_header(local_head, remote_head)
            logger.debug(f"smart.get.{head_comp}: {remote_url}")
            if head_comp == HeadComp.same:
                pass
            elif head_comp == HeadComp.different:
                logger.debug(f"smart.get.{head_comp}: remote={remote_head}")
                logger.debug(f"smart.get.{head_comp}:  local={local_head}")
                self.get(local_url, remote_url)
            elif head_comp == HeadComp.undetermined:
                logger.debug(f"smart.get.{head_comp}: remote={remote_head}")
                logger.debug(f"smart.get.{head_comp}:  local={local_head}")
                self.get(local_url, remote_url)
            else:
                assert False, f"wrong head_comp: {head_comp}"
        else:
            logger.debug(f"smart.get.missing: {remote_url}")
            self.get(local_url, remote_url)

    def smart_put(self, local_url:str, remote_url:str) -> None:
        "upload resource when local-vs-remote headers have changed"
        # TODO
        self.put(local_url, remote_url)


def transport_provider(remote_url: str) -> Provider:
    """
    Provider instance factory.
    """
    remote = urlparse(remote_url)
    if remote.scheme in ('http', 'https'):
        from nspawn.transport import http
        return http.ProviderHttp()
    elif remote.scheme in ('file'):
        from nspawn.transport import file
        return file.ProviderFile()
    else:
        raise RuntimeError(f"Missing transport for url={remote_url}")
