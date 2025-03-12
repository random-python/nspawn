"""
Base engine class
"""

import os
import sys
import abc
import logging
import functools
import jinja2

from typing import Any, List, Iterable

from nspawn import CONFIG
from nspawn.base import token
from nspawn.support.parser import ParseResult
from nspawn.base.profile import ProfileBucket
from nspawn.wrapper.base import Command
from nspawn.support.typing import cached_method
from nspawn.wrapper.sudo import SUDO


def apply_visit(iterable:Iterable):
    for _ in iterable:
        pass


def verify_error(effect_list:List[token.AnyEffect]) -> None:
        error_finder = filter(token.has_type_error, effect_list)
        error_list = list(error_finder)
        if len(error_list) > 0:
            raise RuntimeError(f"Syntax errors: {error_list}")


class Engine(abc.ABC):
    """
    Base engine class
    """

    logger = logging.getLogger(__name__)

    image_url:str = None

    parse_result:ParseResult = None

    script_entry_dir:str = None

    profile_bucket:ProfileBucket = None

    intent_list:List[token.AnyIntent] = []

    shell_invoke = CONFIG.get_list('build', 'shell_invoke')

    def init_args(self, parse_result:ParseResult) -> None:
        assert self.parse_result is None
        self.parse_result = parse_result
        script_path = parse_result.space.script
        self.script_entry_dir = os.path.dirname(script_path)
        self.profile_bucket = ProfileBucket(origin=f"file://{script_path}")

    def source_path(self, effect:token.AnyPathEffect) -> str:
        """
        path for DSL.COPY, DSL.CAST: in the build folder
        convert:
        from logical path: '/etc/config.txt'
        into absolute path: '<build-script-folder>/etc/config.txt'
        """
        return self.script_entry_dir + effect.source

    @abc.abstractclassmethod
    def target_path(self, effect:token.AnyPathEffect) -> str:
        """
        path for DSL.COPY, DSL.CAST: select host vs image
        """

    def invoke_image(self, effect:token.ImageEffect) -> None:
        self.image_url = effect.url

    def invoke_exec(self, effect:token.ExecEffect) -> None:
        self.profile_bucket.with_command(effect.command)

    def invoke_profile(self, effect:token.ProfileEffect) -> None:
        self.profile_bucket.with_bucket_entry_list(effect.bucket_res)

    @cached_method
    def mapper_intent_effect(self) -> token.MappingIntentEffect:
        return token.mapper_intent_effect()

    @abc.abstractclassmethod
    def mapper_effect_invoke(self) -> token.MappingEffectInvoke:
        pass

    @abc.abstractclassmethod
    def invoke_command(self, command:Command) -> None:
        "invoke command on host (during setup) or in the image (during build)"

    def invoke_run(self, effect:token.RunEffect) -> None:
        command = effect.command
        self.invoke_command(command)

    def invoke_shell(self, effect:token.ShellEffect) -> None:
        command = [
            entry.replace("{script}", effect.script)
            for entry in self.shell_invoke
        ]
        self.invoke_command(command)

    def invoke_copy(self, effect:token.CopyEffect) -> None:
        source_path = self.source_path(effect)
        target_path = self.target_path(effect)
        SUDO.files_sync_base(source_path, target_path)

    def invoke_template(self, effect:token.TemplateEffect) -> None:
        source_path = self.source_path(effect)
        target_path = self.target_path(effect)
        source_text = SUDO.file_load(source_path)
        template = jinja2.Template(source_text)
        target_text = template.render(effect.context)
        SUDO.files_sync_base(source_path, target_path)  # copy attr
        SUDO.file_save(target_path, target_text)  # change content
        SUDO.files_sync_time(source_path, target_path)  # copy time

    def parse_intent(self, intent:token.AnyIntent) -> token.AnyEffect:
        mapper = self.mapper_intent_effect()
        return token.parse_intent(intent, mapper)

    def invoke_effect(self, effect:token.AnyEffect) -> Any:
        self.logger.info(effect)
        mapper = self.mapper_effect_invoke()
        return token.invoke_effect(effect, mapper)

    def effect_list(self) -> List[token.AnyEffect]:
        effect_mapper = map(self.parse_intent, self.intent_list)
        effect_list = list(effect_mapper)
        return effect_list

    def register_intent(self, intent:token.AnyIntent) -> None:
        self.intent_list.append(intent)

    def parse_script(self) -> None:
        script_path = self.parse_result.space.script
        self.logger.info(f"Parsing script: {script_path}")
        try:
            script_file = open(script_path, 'r', encoding='utf-8')
            script_text = script_file.read()
            script_file.close()
        except Exception as error:
            self.logger.error(f"Script read error: {error}")
            raise
        try:
            script_code = compile(script_text, script_path, mode='exec')
        except SyntaxError as error:
            self.logger.error(f"Script syntax error: {error}")
            raise
        try:
            script_globals = {}
            script_locals = {}
            script_globals.update(
                __file__=script_path,
            )
            exec(script_code, script_globals, script_locals)
        except Exception as error:
            self.logger.error(f"Script invoke error: {error}")
            raise
        self.logger.info(f"Parsing complete")

    @abc.abstractclassmethod
    def perform_intent(self) -> None:
        pass
