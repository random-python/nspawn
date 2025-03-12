#!/usr/bin/env python3

"""
AWS S3 syncer/tracker
"""

import os
import boto3
import shlex
import logging
import threading
from fnmatch import fnmatch
from dataclasses import dataclass
from typing import List, Callable
from datetime import datetime, timezone
from configparser import ConfigParser

logging.basicConfig(
    level='INFO',
)

logger = logging.getLogger(__name__)


@dataclass
class BotoMeta:
    "local/remote resource meta info"
    entry:str  # relative path
    length: int  # file/object size
    modified:datetime  # file/object time


def convert_time(unix_time:float) -> datetime:
    "map from unix time to python date time"
    unix_secs = int(unix_time)
    base_time = datetime.utcfromtimestamp(unix_secs)
    return base_time.replace(tzinfo=timezone.utc)


class BotoProgress:
    "file transfer progress indicator"

    def __init__(self, entry:str, length:int, perc_step:float=4.0):
        self.lock = threading.Lock()
        self.entry = entry
        self.length = length
        self.perc_step = perc_step
        self.percent = 0.0
        self.count = 0

    def __call__(self, count:int) -> None:
        with self.lock:
            self.count += count
            percent = 100.0 * self.count / self.length
            if percent - self.percent > self.perc_step:
                self.percent = percent
                display = round(percent, 1)
                logger.info(f"  {self.entry} @ {display}%")


class BotoSync:
    """
    AWS S3 syncer
    """

    store_dir:str
    bucket_name:str
    bucket_mode:str
    include_list:List[str]
    exclude_list:List[str]
    use_expire:bool
    expire_days:int

    res_s3:object
    bucket_res:object

    def __init__(self,
            store_dir:str,
            bucket_name:str='image-server',
            bucket_mode:str='public-read',
            include_list:str='',
            exclude_list:str='',
            use_expire:bool=True,
            expire_days:int=60,
        ):
        self.store_dir = store_dir
        self.bucket_name = bucket_name
        self.bucket_mode = bucket_mode
        self.include_list = shlex.split(include_list)
        self.exclude_list = shlex.split(exclude_list)
        self.use_expire = use_expire
        self.expire_days = expire_days
        #
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
        "discover remote object meta data"
        try:
            head_object = self.res_s3.meta.client.head_object(
                Bucket=self.bucket_name,
                Key=entry,
            )
            meta_data = head_object['Metadata']
            return BotoMeta(
                entry=entry,
                length=int(meta_data['entry_length']),
                modified=datetime.fromisoformat(meta_data['entry_modified']),
            )
        except:
            return None

    def visit_bucket(self, action:Callable=lambda entry: print(entry)):
        "apply action to remote bucket"
        # TODO

    def visit_store(self, action:Callable=lambda entry: print(entry)):
        "apply action to local storage"
        for base, dir_list, file_list in os.walk(self.store_dir):
            for file in file_list:
                path = f"{base}/{file}"
                entry = os.path.relpath(path, self.store_dir)
                action(entry)

    def has_match(self, entry:str) -> bool:
        "match entry aginst include/exclude"
        has_match = False
        for include in self.include_list:
            if fnmatch(entry, include):
                has_match = True
        for exclude in self.exclude_list:
            if fnmatch(entry, exclude):
                has_match = False
        return has_match

    def perform_drop(self, entry:str) -> None:
        "expire local image resources"
        if not self.has_match(entry):
            logger.info(f"no match: {entry}")
            return
        local = self.local_meta(entry)
        if local:
            current = datetime.now().astimezone(timezone.utc)
            modified = local.modified
            delta_time = current - modified
            delta_days = delta_time.days
            if  delta_days >= self.expire_days:
                logger.info(f"exipre: {entry}")
                local_path = self.local_path(entry)
                os.remove(local_path)
            else:
                logger.info(f"retain: {entry} delta_days={delta_days}")

    def perform_full_drop(self):
        "expire local image resources"
        if self.use_expire:
            logger.info(f"use expire")
            self.visit_store(self.perform_drop)
        else:
            logger.info(f"no use expire")

    def perform_sync(self, entry:str) -> None:
        "sinchronize single entry: store file <-> bucket object"
        if not self.has_match(entry):
            logger.info(f"no match: {entry}")
            return
        local = self.local_meta(entry)
        remote = self.remote_meta(entry)
        if not local and not remote:
            logger.warining(f"no entry: {entry}")
            pass
        if local and not remote:
            logger.info(f"upload: local: {local}")
            self.entry_put(entry)
        elif not local and remote:
            logger.info(f"download: remote: {remote}")
            self.entry_get(entry)
        elif local and remote:
            if local == remote:
                logger.info(f"in sync: entry: {local}")
                pass
            elif local.modified > remote.modified:
                logger.info(f"upfresh: local: {local} remote: {remote}")
                self.entry_put(entry)
            elif local.modified < remote.modified:
                logger.info(f"downfresh: local: {local} remote: {remote}")
                self.entry_get(entry)

    def perform_full_sync(self):
        "synchronize storage and bucket"
        self.visit_store(self.perform_sync)

    def entry_get(self, entry:str) -> None:
        "transfer remote object into local file"
        logger.warining(f"entry_get: {entry} :: TODO")

    def entry_put(self, entry:str) -> None:
        "transfer local file into remote object"
        try:
            local = self.local_meta(entry)
            extra_args = dict(
                ACL=self.bucket_mode,
                Metadata=dict(
                    entry_length=str(local.length),
                    entry_modified=local.modified.isoformat(),
                )
            )
            self.res_s3.meta.client.upload_file(
                Filename=self.local_path(entry),
                Bucket=self.bucket_name,
                Key=entry,
                ExtraArgs=extra_args,
                Callback=BotoProgress(entry, local.length),
            )
        except Exception as error:
            logger.error(f"upload error: {error} @ {entry}")

#
#
#


def invoke_module():

    this_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = f"{this_dir}/sync.ini"
    config_parser = ConfigParser()
    config_parser.read(config_path)
    config_bucket = config_parser['bucket']

    os.environ['AWS_CONFIG_FILE'] = config_bucket["service_sync_config"]

    boto_sync = BotoSync(
        store_dir=config_bucket["service_store_dir"],
        bucket_name=config_bucket["service_bucket_name"],
        bucket_mode=config_bucket["service_bucket_mode"],
        include_list=config_bucket["service_include_list"],
        exclude_list=config_bucket["service_exclude_list"],
        use_expire=config_bucket.getboolean("service_use_expire"),
        expire_days=int(config_bucket["service_expire_days"]),
    )

    boto_sync.perform_full_drop()
    boto_sync.perform_full_sync()


if __name__ == "__main__":
    invoke_module()
