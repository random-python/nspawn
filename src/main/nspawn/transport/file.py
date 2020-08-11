
import logging
from typing import Mapping
from urllib.parse import urlparse

from nspawn.transport import base
from nspawn.wrapper.sudo import SUDO
from nspawn.support.header import synchronize_header, discover_header

logger = logging.getLogger(__name__)


class ProviderFile(base.Provider):

    def remote_head(self, remote_url:str) -> Mapping[str, str]:
        "extract path metadata stored in xattr"
        return discover_header(remote_url)

    def get(self, local_url:str, remote_url:str) -> None:
        logger.debug(f"file.get.fetch: {remote_url}")
        local, remote = self.parse(local_url, remote_url)
        SUDO.files_sync_full(remote.path, local.path)
        synchronize_header(remote.path, local.path)

    def put(self, local_url:str, remote_url:str) -> None:
        logger.debug(f"file.put.upload: {remote_url}")
        local, remote = self.parse(local_url, remote_url)
        SUDO.files_sync_full(local.path, remote.path)
        synchronize_header(local.path, remote.path)
