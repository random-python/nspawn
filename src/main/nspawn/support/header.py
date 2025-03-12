"""
HTTP transport headers
"""

import os
import enum
from typing import Mapping
from datetime import datetime, timezone

from nspawn.support.parser import parse_unquote
from nspawn.wrapper.sudo import SUDO
from builtins import dict
from urllib.parse import urlparse


@enum.unique
class Header(enum.Enum):
    "http content comaprison headers"

    # standard
    etag = "etag"
    last_modified = "last-modified"
    content_length = "content-length"

    # custom
    nspawn_digest = "nspawn-digest"

    def __repr__(self) -> str:
        return self.value

    def __get__(self, *_) -> str:
        return self.value


@enum.unique
class HeadComp(enum.Enum):
    "header comparison result"

    same = "same"
    different = "different"
    undetermined = "undetermined"


def compare_header(local_head:dict, remote_head:dict) -> HeadComp:
    "compare http headers to determine content identity"
    # custom header
    has_digest = Header.nspawn_digest in local_head and Header.nspawn_digest in remote_head
    if has_digest:
        match_digest = local_head[Header.nspawn_digest] == remote_head[Header.nspawn_digest]
        if match_digest:
            return HeadComp.same
        else:
            return HeadComp.different
    # etag header
    has_etag = Header.etag in local_head and Header.etag in remote_head
    if has_etag:
        match_etag = parse_unquote(local_head[Header.etag]) == parse_unquote(remote_head[Header.etag])
        if match_etag:
            return HeadComp.same
        else:
            return HeadComp.different
    # both last_modified and content_length headers
    has_last_modified = Header.last_modified in local_head and Header.last_modified in remote_head
    has_content_length = Header.content_length in local_head and Header.content_length in remote_head
    if has_last_modified and has_content_length:
        match_time = local_head[Header.last_modified] == remote_head[Header.last_modified]
        match_size = local_head[Header.content_length] == remote_head[Header.content_length]
        if match_time and match_size:
            return HeadComp.same
        else:
            return HeadComp.different
    # catch all case
    return HeadComp.undetermined


def synchronize_header(source:str, target:str) -> None:
    "transfer header metadata between local paths"
    header_dict = dict()  # never empty
    try:
        header_dict = SUDO.xattr_load(source)
    except:
        pass
    if not header_dict:
        header_dict = produce_header(source)
    try:
        SUDO.xattr_save(target, header_dict)
    except:
        SUDO.files_sync_time(source, target)


def convert_time(unix_time:float) -> datetime:
    "map from unix time to python date time"
    unix_secs = int(unix_time)
    base_time = datetime.utcfromtimestamp(unix_secs)
    return base_time.replace(tzinfo=timezone.utc)


def produce_header(local_path:str) -> Mapping[str, str]:
    "extract header meta data from local path"
    last_modified = convert_time(os.path.getmtime(local_path))
    content_length = os.path.getsize(local_path)
    header_dict = {
        Header.last_modified : last_modified.isoformat(),
        Header.content_length : str(content_length),
    }
    return header_dict


def discover_header(local_url:str) -> Mapping[str, str]:
    "obtain meta description of local resource"
    local = urlparse(local_url)
    header_dict = dict()  # never empty
    try:
        header_dict = SUDO.xattr_load(local.path)
    except:
        pass
    if not header_dict:
        header_dict = produce_header(local.path)
    return header_dict
