"""
"""

import os
import sys
import atexit
import functools
from typing import List, Iterable

from nspawn.base import engine
from nspawn.base import profile
from nspawn.base import token

from nspawn.base.image import (
    ImageMeta, ImageStore, ImageTypeNspawn,
    perform_image_move,
    image_store_from_url,
    perform_image_erase_host,
    perform_image_put_steps,
    perform_image_put_context,
 )
from nspawn.base.machine import (
    MachineResult, MachineMeta,
    perform_exec_create,
    perform_exec_delete,
    machine_result_from_image,
    perform_machine_runtime_erase,
  )
from nspawn.base.overlay import (
    ResourceOverlay,
    perform_overlay_from_url,
)

from nspawn.tool.stamp import build_stamp

from nspawn.wrapper.sudo import SUDO
from nspawn.wrapper.systemd_nspawn import SYSTEMD_NSPAWN
from builtins import isinstance
from nspawn import CONFIG
from nspawn.transport.base import transport_provider
from nspawn.support.files import make_temp_path
from nspawn.support.typing import cached_method
from nspawn.support.proxy import discover_proxy_config
from nspawn.packer.base import packer_provider


def has_destroy_build_dir() -> bool:
    return not CONFIG['build'].getboolean('preserve_build_dir')


class BuildEgine(engine.Engine):

    build_id:str = None

    build_url:str = None
    build_image:ImageStore = None

#     image_store:ImageStore = None

    overlay_url_list:List[str] = []

    machine_result:MachineResult = None

    def __init__(self):
        build_space = CONFIG['build']['build_space']
        self.build_id = f"{build_space}-{build_stamp()}"

    def build_option_list(self) -> List[str]:
        return self.profile_bucket.render_option_list(
            quote="",
            select=lambda entry : isinstance(entry, profile.BuildType),
        )

    def proxy_option_list(self) -> List[str]:
        "inject proxy environment variables during machine build"
        option_list = []
        use_machine_proxy = CONFIG['proxy'].getboolean('use_machine_proxy')
        if use_machine_proxy:
            proxy_config = discover_proxy_config()
            entry_list = proxy_config.into_entry_list()
            for entry in entry_list:
                option = f'--setenv={entry}'
                option_list.append(option)
        return option_list

    def machine_create(self) -> None:

        # unique host name in archive/extract
        self.build_url = f"file://{self.build_id}"
        image_type = ImageTypeNspawn
        image_meta = ImageMeta(
            self.build_url,
            self.overlay_url_list,
            profile_command=self.profile_bucket.command,
            profile_entry_list=self.profile_bucket.render_entry_list(),
        )

        self.build_image = image_store_from_url(self.build_url)
        self.build_image = self.build_image.with_image_type(image_type).with_image_meta(image_meta)
        perform_image_put_context(self.build_image)

        machine_name = self.build_id
        machine_template = CONFIG['machine']['template']
        machine_meta = MachineMeta(machine_name, machine_template)

        self.machine_result = machine_result_from_image(self.build_image, machine_meta)

        perform_exec_create(self.machine_result)

        if has_destroy_build_dir():
            atexit.register(perform_image_erase_host, self.build_image)
            atexit.register(perform_machine_runtime_erase, self.machine_result)

    def machine_delete(self) -> None:
        perform_exec_delete(self.machine_result)

    def machine_path(self, logical_path:str) -> str:
        """ convert
        from logical path: '/etc/config.txt'
        into machine absolute mount path: '/var/lib/machines/<machine>/etc/config.txt'
        """
        machine_directory = self.machine_result.machine_directory()
        return machine_directory + logical_path

    def target_path(self, effect:token.AnyPathEffect) -> str:
        "path for DSL.COPY, DSL.CAST: in the image"
        return self.machine_path(effect.target)

    def runtime_path(self, logical_path:str) -> str:
        """ convert
        from logical path: '/etc/config.txt'
        into runtime absolute path: '/var/lib/nspawn/tempdir/build-<guid>/root/etc/config.txt'
        """
        runtime_root = self.machine_result.machine_store.root_dir()
        return runtime_root + logical_path

    def extract_path(self, logical_path:str) -> str:
        """ convert
        from logical path: '/etc/config.txt'
        into image extract absolute path: '/var/lib/nspawn/extract/build-<guid>/etc/config.txt'
        """
        return self.build_image.extract_path() + logical_path

    def invoke_pull(self, effect:token.PullEffect) -> None:
        perform_overlay_from_url(effect.url, resource_overlay=ResourceOverlay())
        self.overlay_url_list.append(effect.url)

    # TODO use persistendt archive/extract
    def invoke_fetch(self, effect:token.FetchEffect) -> None:
        remote_url = effect.url
        package_name = os.path.basename(remote_url)
        fetch_archive = make_temp_path('fetch-archive') + '-' + package_name
        fetch_extract = make_temp_path('fetch-extract') + '-' + package_name
        # download
        transport = transport_provider(remote_url)
        transport.get(fetch_archive, remote_url)
        # extract
        packer = packer_provider(remote_url)
        packer.extract(fetch_archive, fetch_extract)
        # move
        source_path = fetch_extract + '/' + effect.source
        target_path = self.runtime_path(effect.target)
        SUDO.files_move(source_path, target_path)
        # clean
        SUDO.files_delete(fetch_archive)
        SUDO.files_delete(fetch_extract)

    def invoke_command(self, command:List[str]) -> None:
        "invoke command inside the image runtime"
        machine = self.build_id
        build_command = self.build_option_list() + self.proxy_option_list() + command
        result = SYSTEMD_NSPAWN.execute_flow(machine, build_command)
        result.assert_return()

    def invoke_push(self, effect:token.PushEffect) -> None:
        #
        assert self.image_url
        #
        source_image = self.build_image
        target_image = image_store_from_url(self.image_url)
        perform_image_move(source_image, target_image)
        #
        image_type = ImageTypeNspawn
        image_meta = ImageMeta(
            image_url=self.image_url,
            overlay_url_list=self.overlay_url_list,
            profile_command=self.profile_bucket.command,
            profile_entry_list=self.profile_bucket.render_entry_list(),
        )
        target_image = target_image.with_image_type(image_type).with_image_meta(image_meta)
        #
        runtime_root = self.runtime_path('/')
        extract_root = target_image.extract_path()
        SUDO.files_sync_full(runtime_root, extract_root)
        #
        perform_image_put_steps(target_image)

    @cached_method
    def mapper_effect_invoke(self) -> token.MappingEffectInvoke:
        mapper = dict([
            (token.ImageEffect, self.invoke_image),
            (token.PullEffect, self.invoke_pull),
            (token.ExecEffect, self.invoke_exec),
            (token.ProfileEffect, self.invoke_profile),
            (token.FetchEffect, self.invoke_fetch),
            (token.CopyEffect, self.invoke_copy),
            (token.TemplateEffect, self.invoke_template),
            (token.RunEffect, self.invoke_run),
            (token.ShellEffect, self.invoke_shell),
            (token.PushEffect, self.invoke_push),
        ])
        return mapper

    def perform_intent(self) -> None:

        self.logger.info("Performing build")

        effect_list = self.effect_list()
        engine.verify_error(effect_list)

        declare_finder = filter(token.has_type_declare, effect_list)
        execute_finder = filter(token.has_type_execute, effect_list)
        publish_finder = filter(token.has_type_publish, effect_list)

        declare_mapper = map(self.invoke_effect, declare_finder)
        execute_mapper = map(self.invoke_effect, execute_finder)
        publish_mapper = map(self.invoke_effect, publish_finder)

        engine.apply_visit(declare_mapper)

        try:
            self.machine_create()
            engine.apply_visit(execute_mapper)
            engine.apply_visit(publish_mapper)
        finally:
            self.machine_delete()

        self.logger.info("Build complete")


ENGINE = BuildEgine()
