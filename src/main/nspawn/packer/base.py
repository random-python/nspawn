"""
Base type for packer provider.
"""

import abc
import logging
from typing import List, Mapping
from urllib.parse import urlparse

from nspawn.wrapper.sudo import SUDO
from nspawn.support.header import compare_header, HeadComp, discover_header

logger = logging.getLogger(__name__)


class Provider(abc.ABC):
    """
    Base type for packer provider.
    """

    @classmethod
    @abc.abstractmethod
    def suffix_list(cls) -> List[str]:
        "provide packer discovery"

    @abc.abstractmethod
    def archive(self, archive_path:str, extract_path:str) -> None:
        "make archive from extract"

    @abc.abstractmethod
    def extract(self, archive_path:str, extract_path:str) -> None:
        "make extract from archive"

    def smart_archive(self, archive_path:str, extract_path:str) -> None:
        "make archive from extract, when needed"
        # TODO
        self.archive(archive_path, extract_path)

    def smart_extract(self, archive_path:str, extract_path:str) -> None:
        "make extract from archive, when needed"
        if SUDO.folder_check(extract_path):
            logger.debug(f"smart.extract.present: {extract_path}")
            archive_head = discover_header(archive_path)
            extract_head = discover_header(extract_path)
            head_comp = compare_header(archive_head, extract_head)
            logger.debug(f"smart.extract.{head_comp}: {extract_path}")
            if head_comp == HeadComp.same:
                pass
            elif head_comp == HeadComp.different:
                logger.debug(f"smart.extract.{head_comp}: archive={archive_head}")
                logger.debug(f"smart.extract.{head_comp}: extract={extract_head}")
                self.extract(archive_path, extract_path)
            elif head_comp == HeadComp.undetermined:
                logger.debug(f"smart.extract.{head_comp}: archive={archive_head}")
                logger.debug(f"smart.extract.{head_comp}: extract={extract_head}")
                self.extract(archive_path, extract_path)
            else:
                assert False, f"wrong head_comp: {head_comp}"
        else:
            logger.debug(f"smart.extract.missing: {extract_path}")
            self.extract(archive_path, extract_path)


def packer_provider(url:str) -> Provider:
    "discover archive/extract provider based on url"

    remote = urlparse(url)

    from nspawn.packer.tar import ProviderTar
    from nspawn.packer.zip import ProviderZip

    provider_class_list = [
        ProviderTar,
        ProviderZip,
    ]

    for provider_class in provider_class_list:
        if remote.path.endswith(tuple(provider_class.suffix_list())):
            provider_instance = provider_class()
            return provider_instance

    raise RuntimeError(f'no packer for url={url}')
