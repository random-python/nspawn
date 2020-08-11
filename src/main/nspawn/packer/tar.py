"""
"""

import os
import logging
from typing import List

from nspawn import CONFIG
from nspawn.packer.base import Provider
from nspawn.support.files import make_temp_path
from nspawn.wrapper.sudo import SUDO
from nspawn.wrapper.tar import Tar
from nspawn.support.header import synchronize_header

logger = logging.getLogger(__name__)


class ProviderTar(Provider):

    @classmethod
    def suffix_list(cls) -> List[str]:
        return CONFIG.get_list('wrapper/tar', 'suffix_list')

    def archive(self, archive_path:str, extract_path:str) -> None:
        logger.debug(f"pack.archive.tar: {extract_path}")
        SUDO.folder_assert(extract_path)
        archive_temp = make_temp_path("tar-archive-temp")
        SUDO.parent_ensure(archive_temp)
        tar = Tar()
        tar.with_archive(archive_temp)
        tar.with_extract(extract_path)
        tar.with_packer(archive_path)
        tar.with_make_pack()  # keep last
        tar.execute_unit_sert()
        SUDO.files_move(archive_temp, archive_path)
        synchronize_header(extract_path, archive_path)

    def extract(self, archive_path:str, extract_path:str) -> None:
        logger.debug(f"pack.extract.tar: {extract_path}")
        SUDO.file_assert(archive_path)
        extract_temp = make_temp_path("tar-extract-temp")
        SUDO.folder_ensure(extract_temp)
        tar = Tar()
        tar.with_archive(archive_path)
        tar.with_extract(extract_temp)
        tar.with_packer(archive_path)
        tar.with_make_unpack()  # keep last
        tar.execute_unit_sert()
        if SUDO.folder_check(extract_path):
            # user rsync to preserve active machines
            SUDO.files_sync_full(extract_temp, extract_path)
            SUDO.files_delete(extract_temp)
        else:
            # user move for efficiency
            SUDO.files_move(extract_temp, extract_path)
        synchronize_header(archive_path, extract_path)
