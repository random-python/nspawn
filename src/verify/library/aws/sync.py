#!/usr/bin/env python3

"""
AWS S3 syncer
"""

import os
import logging
import threading
from typing import Callable
from datetime import datetime
from dateutil.tz.tz import tzutc
from dataclasses import dataclass

import boto3

logger = logging.getLogger(__name__)

logging.basicConfig(
    level='INFO',
)


@dataclass
class BotoMeta:
    "resource meta info"
    entry:str  # relative file path
    length: int  # local file size
    modified:datetime  # local file time


def convert_time(unix_time:float) -> datetime:
    "map from unix time to date time"
    unix_secs = int(unix_time)
    base_time = datetime.utcfromtimestamp(unix_secs)
    return base_time.replace(tzinfo=tzutc())


class BotoProgress:
    "transfer progress indicator"

    def __init__(self, entry:str, length:int):
        self.lock = threading.Lock()
        self.entry = entry
        self.length = length
        self.percent = 0.0
        self.count = 0

    def __call__(self, count:int) -> None:
        with self.lock:
            self.count += count
            percent = 100.0 * self.count / self.length
            if percent - self.percent > 4:
                self.percent = percent
                display = round(percent, 2)
                logger.info(f"--- {self.entry} @ {display}%")


class BotoSync:
    """
    AWS S3 syncer
    """

    store_dir:str
    bucket_name:str
    bucket_mode:str
    res_s3:object
    bucket_res:object

    def __init__(self,
            store_dir:str,
            bucket_name:str,
            bucket_mode:str='public-read',
        ):
        self.store_dir = store_dir
        self.bucket_name = bucket_name
        self.bucket_mode = bucket_mode
        self.res_s3 = boto3.resource('s3')
        self.bucket_res = self.res_s3.Bucket(bucket_name)

    def local_path(self, entry:str) -> str:
        "produce absolute file path"
        return f"{self.store_dir}/{entry}"

    def local_meta(self, entry:str) -> BotoMeta:
        "discover local file meta data"
        path = self.local_path(entry)
        if os.path.isfile(path):
            return BotoMeta(
                entry=entry,
                length=os.path.getsize(path),
                modified=convert_time(os.path.getmtime(path))
            )
        else:
            return None

    def remote_meta(self, entry:str) -> BotoMeta:
        "discover remote file meta data"
        try:
            head_object = self.res_s3.meta.client.head_object(
                Bucket=self.bucket_name,
                Key=entry,
            )
            meta_data = head_object['Metadata']
            return BotoMeta(
                entry=entry,
                length=int(meta_data['local_length']),
                modified=datetime.fromisoformat(meta_data['local_modified']),
            )
        except:
            return None

    def visit_store(self, action:Callable=lambda entry: print(entry)):
        "apply action to the storage"
        for base, dir_list, file_list in os.walk(self.store_dir):
            for file in file_list:
                path = f"{base}/{file}"
                entry = os.path.relpath(path, self.store_dir)
                action(entry)

    def perform_sync(self, entry:str) -> None:
        "sinchronize single file entry"
        local = self.local_meta(entry)
        remote = self.remote_meta(entry)
        logger.debug(f"local {local}")
        logger.debug(f"remote {remote}")
        if not local and not remote:
            logger.info(f"invalid: {entry}")
            pass
        if local and not remote:
            logger.info(f"upload: {entry}")
            self.entry_put(entry)
        elif not local and remote:
            logger.warning(f"no local: {entry}")
            pass
        elif local and remote:
            if local == remote:
                logger.info(f"match: {entry}")
                pass
            elif local.modified > remote.modified:
                logger.info(f"upfresh: {entry}")
                self.entry_put(entry)
            elif local.modified < remote.modified:
                logger.warning(f"local is older: {entry}")
                pass

    def perform_full_sync(self):
        self.visit_store(self.perform_sync)

    def entry_put(self, entry:str) -> None:
        try:
            local = self.local_meta(entry)
            extra_args = dict(
                ACL=self.bucket_mode,
                Metadata=dict(
                    local_length=str(local.length),
                    local_modified=local.modified.isoformat(),
                )
            )
            self.res_s3.meta.client.entry_put(
                Filename=self.local_path(entry),
                Bucket=self.bucket_name,
                Key=entry,
                ExtraArgs=extra_args,
                Callback=BotoProgress(entry, local.length),
            )
        except Exception as error:
            logger.error(f"upload error: {error} @ {entry}")

    def download_file(self, entry:str) -> None:
        "TODO"

#
#
#


this_dir = os.path.dirname(os.path.abspath(__file__))

store_dir = f"{this_dir}/store"
bucket_name = 'image.carrotgarden.com'

boto_sync = BotoSync(store_dir, bucket_name)
boto_sync.perform_full_sync()
