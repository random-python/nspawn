"""
Image archive/extract operations
"""

import yaml
import functools

from dataclasses import dataclass, replace, asdict, field

from typing import List
from urllib.parse import urlparse, urlunparse, ParseResult

from nspawn.packer.base import packer_provider
from nspawn.transport.base import transport_provider
from nspawn.wrapper.sudo import SUDO

from nspawn import CONFIG
from nspawn.wrapper.base import Command


def image_archive_root():
    return CONFIG['storage']['archive']


def image_extract_root():
    return CONFIG['storage']['extract']


@dataclass(frozen=True)
class ImageMeta:
    image_url:str
    overlay_url_list:List[str] = field(default_factory=list)
    profile_command:Command = field(default=None)
    profile_entry_list:List[str] = field(default_factory=list)


def image_meta_encode(image_meta:ImageMeta) -> str:
    meta_dict = asdict(image_meta)
    return yaml.dump(meta_dict)


def image_meta_decode(text:str) -> ImageMeta:
    meta_dict = yaml.safe_load(text)
    return ImageMeta(
        image_url=meta_dict["image_url"],
        overlay_url_list=meta_dict["overlay_url_list"],
        profile_command=meta_dict["profile_command"],
        profile_entry_list=meta_dict["profile_entry_list"],
    )


def image_meta_load(file:str) -> ImageMeta:
    text = SUDO.file_load(file)
    return image_meta_decode(text)


def image_meta_save(file:str, image_meta:ImageMeta) -> None:
    text = image_meta_encode(image_meta)
    SUDO.file_save(file, text)


@dataclass(frozen=True)
class ImageType:
    name:str
    root_path:str
    meta_path:str

    def has_root(self):
        return self.root_path is not None

    def has_meta(self):
        return self.meta_path is not None


ImageTypeNspawn = ImageType(
    name="Native nspawn image",
    root_path="/",
    meta_path="/nspawn-image.yaml",
)

ImageTypeArchIso = ImageType(
    name="ArchLinux ISO",
    root_path="/root.x86_64",
    meta_path=None,
)

ImageTypeDefault = ImageType(
    name="Default Image",
    root_path="/",
    meta_path=None,
)

image_type_list = [
    ImageTypeNspawn,
    ImageTypeArchIso,
    ImageTypeDefault,
]


def image_type_form(extract_path:str) -> ImageType:
    for entry in image_type_list:
        has_root = False
        if entry.root_path is None:
            has_root = True
        else:
            root_path = extract_path + entry.root_path
            has_root = SUDO.folder_check(root_path)
        has_meta = False
        if entry.meta_path is None:
            has_meta = True
        else:
            meta_path = extract_path + entry.meta_path
            has_meta = SUDO.file_check(meta_path)
        if has_root and has_meta:
            return entry
    raise Exception(f"missing type for {extract_path}")


@dataclass(frozen=True, eq=True)
class ImageStore:
    """
    image resources representation
    """
    url:str = field(hash=True)
    archive_root:str = field(repr=False)
    extract_root:str = field(repr=False)
    image_meta:ImageMeta = field(repr=True, default=None)
    image_type:ImageType = field(repr=True, default=None)

    def url_bean(self) -> ParseResult:
        return urlparse(self.url)

    def resource_root(self) -> str:
        bean = self.url_bean()
        return f"/{bean.hostname}"

    def resource_path(self) -> str:
        bean = self.url_bean()
        return f"/{bean.hostname}{bean.path}"

    def has_meta(self) -> bool:
        return self.image_meta is not None

    def has_type(self) -> bool:
        return self.image_type is not None

    def has_archive(self) -> bool:
        return SUDO.file_check(self.archive_path())

    def has_extract(self) -> bool:
        return SUDO.folder_check(self.extract_path())

    def archive_host(self) -> str:
        return self.archive_root + self.resource_root()

    def extract_host(self) -> str:
        return self.extract_root + self.resource_root()

    def archive_path(self) -> str:
        return self.archive_root + self.resource_path()

    def extract_path(self) -> str:
        return self.extract_root + self.resource_path()

    def with_image_meta(self, image_meta:ImageMeta):
        return replace(self, image_meta=image_meta)

    def with_image_type(self, image_type:ImageType):
        return replace(self, image_type=image_type)

    def image_root(self) -> str:
        return self.extract_path() + self.image_type.root_path


def image_store_from_url(url:str) -> ImageStore:
    image_store = ImageStore(url, image_archive_root(), image_extract_root())
    return image_store


def perform_image_get(url:str) -> ImageStore:
    image_store = image_store_from_url(url)
    image_store = perform_image_get_steps(image_store)
    return image_store


@functools.lru_cache()  # cache based on image_store.url
def perform_image_get_steps(image_store:ImageStore) -> ImageStore:
    image_store = perform_image_get_archive(image_store)
    image_store = perform_image_get_extract(image_store)
    image_store = perform_image_get_context(image_store)
    return image_store


def perform_image_get_archive(image_store:ImageStore) -> ImageStore:
    provider = transport_provider(image_store.url)
    provider.smart_get(image_store.archive_path(), image_store.url)
    assert image_store.has_archive(), f"transport get failure: {image_store.url}"
    return image_store


def perform_image_get_extract(image_store:ImageStore) -> ImageStore:
    provider = packer_provider(image_store.url)
    provider.smart_extract(image_store.archive_path(), image_store.extract_path())
    assert image_store.has_extract(), f"packer extract failure: {image_store.url}"
    return image_store


def perform_image_get_context(image_store:ImageStore) -> ImageStore:
    image_type = image_type_form(image_store.extract_path())
    image_meta = None
    if image_type.has_meta():
        meta_path = image_store.extract_path() + image_type.meta_path
        image_meta = image_meta_load(meta_path)
    else:
        image_meta = ImageMeta(image_url=image_store.url)
    image_store = image_store.with_image_type(image_type).with_image_meta(image_meta)
    return image_store


def perform_image_put_steps(image_store:ImageStore) -> None:
    perform_image_put_context(image_store)
    perform_image_put_extract(image_store)
    perform_image_put_archive(image_store)


def perform_image_put_context(image_store:ImageStore) -> None:
    if image_store.has_type() and image_store.has_meta():
        image_type = image_store.image_type
        image_meta = image_store.image_meta
        meta_path = image_store.extract_path() + image_type.meta_path
        image_meta_save(meta_path, image_meta)


def perform_image_put_extract(image_store:ImageStore) -> None:
    provider = packer_provider(image_store.url)
    provider.archive(image_store.archive_path(), image_store.extract_path())


def perform_image_put_archive(image_store:ImageStore) -> None:
    provider = transport_provider(image_store.url)
    provider.put(image_store.archive_path(), image_store.url)


def perform_image_move(source:ImageStore, target:ImageStore) -> None:
    if source.has_archive():
        SUDO.files_move(source.archive_path(), target.archive_path())
    if source.has_extract():
        SUDO.files_move(source.extract_path(), target.extract_path())


def perform_image_erase_host(image_store:ImageStore) -> None:
    SUDO.files_delete(image_store.archive_host())
    SUDO.files_delete(image_store.extract_host())


def perform_image_erase_path(image_store:ImageStore) -> None:
    SUDO.files_delete(image_store.archive_path())
    SUDO.files_delete(image_store.extract_path())
