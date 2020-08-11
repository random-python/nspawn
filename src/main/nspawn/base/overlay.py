"""
Resource overlay operations
"""

from typing import List, Deque, Iterable
from collections import deque
from dataclasses import dataclass, field

from nspawn.base.image import (
    ImageStore, ImageMeta,
    image_store_from_url,
    perform_image_get_steps,
)
from nspawn.wrapper.base import Command
from nspawn.base import profile
from nspawn.base.profile import AnyEntry


@dataclass
class ResourceOverlay:
    """
    Machine image dependency list representation
    """

    image_store_list:Deque[ImageStore] = field(default_factory=deque)

    def __str__(self):
        return f"{self.image_store_list}"

    def has_image_store(self, image_entry:ImageStore) -> bool:
        for image_store in self.image_store_list:
            if image_store.url == image_entry.url:
                return True
        return False

    def collect_image_store(self, image_entry:ImageStore) -> None:
        if not self.has_image_store(image_entry):
            self.image_store_list.appendleft(image_entry)

    def image_root_list(self) -> List[str]:
        extract = map(ImageStore.image_root, self.image_store_list)
        produce = list(extract)
        return produce

    def image_meta_list(self) -> List[ImageMeta]:
        select = lambda store : store.image_meta
        extract = map(select, self.image_store_list)
        cleanup = filter(None, extract)
        return list(cleanup)

    def render_root_path(self) -> str:
        image_root_list = self.image_root_list()
        return ":".join(image_root_list)

    def render_profile_command(self) -> Command:
        select = lambda meta : meta.profile_command
        extract = map(select, self.image_meta_list())
        cleanup = filter(None, extract)
        produce = list(cleanup)
        if produce:
            return produce[0]
        else:
            return None

    def profile_entry_list(self) -> List[AnyEntry]:
        entry_list = []
        for image_meta in self.image_meta_list():
            origin = image_meta.image_url
            entry_token_list = image_meta.profile_entry_list
            for entry_token in entry_token_list:
                entry = profile.parse_profile_entry(entry_token, origin)
                entry_list.append(entry)
        return entry_list

    def render_profile_option_list(self, quote="") -> List[str]:
        option_list = []
        entry_list = self.profile_entry_list()
        for entry in entry_list:
            option = entry.render_option(quote=quote)
            option_list.append(option)
        return option_list


def perform_overlay_from_url(image_url:str, resource_overlay:ResourceOverlay) -> None:
    "recursively collect image dpendencies into overlay list"
    image_store = image_store_from_url(image_url)
    image_store = perform_image_get_steps(image_store)
    perform_overlay_from_image(image_store, resource_overlay)


def perform_overlay_from_image(image_store:ImageStore, resource_overlay:ResourceOverlay) -> None:
    "recursively collect image dpendencies into overlay list"
    image_meta = image_store.image_meta
    overlay_url_list = image_meta.overlay_url_list
    for overlay_url in overlay_url_list :
        perform_overlay_from_url(overlay_url, resource_overlay)
    resource_overlay.collect_image_store(image_store)
