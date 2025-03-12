import sys
import time
import logging
import functools
from typing import List, Mapping, Callable
from nspawn.base import engine
from nspawn.base import token
from nspawn.app.engine.parser import SetupAction
from nspawn.base.machine import (
    machine_result_from_url,
    perform_machine_create,
    perform_machine_delete,
    MachineMeta,
)
from nspawn.wrapper.sudo import SUDO
from nspawn.wrapper.nsenter import NSENTER
from nspawn.wrapper.systemctl import SYSTEM_CTL
from nspawn.wrapper.machinectl import MACHINE_CTL
from nspawn.support.typing import cached_method
from nspawn.wrapper.base import Command

from jinja2 import Template


class SetupEgine(engine.Engine):

    machine_meta:MachineMeta = None

    command_list:List[Command] = []

    def machine_name(self) -> str:
        return f"{self.machine_meta.machine_name}"

    def service_name(self) -> str:
        return f"{self.machine_name()}.service"

    def target_path(self, effect:token.AnyPathEffect) -> str:
        "path for DSL.COPY, DSL.CAST: on the host"
        return effect.target

    def invoke_machine(self, effect:token.MachineEffect) -> None:
        self.machine_meta = MachineMeta(
            machine_name=effect.name,
            machine_template=effect.template,
            unit_conf=effect.unit_conf,
            service_conf=effect.service_conf,
            install_conf=effect.install_conf,
        )

    def invoke_command(self, command:Command) -> None:
        self.command_list.append(command)

    def perform_command(self) -> None:
        "invoke command on the host"
        self.logger.debug("perform_command")
        for command in self.command_list:
            self.logger.info(f"Command: {command}")
            result = SUDO.execute_flow(command)
            result.assert_return()

    def perform_update(self) -> None:
        self.logger.debug("perform_update")
        self.perform_desure()
        self.machine_await(present=False)
        self.perform_ensure()

    def perform_with_status(self, perform_func) -> None:
        try:
            perform_func()
        except AssertionError as error:
            result = SYSTEM_CTL.status(self.service_name())
            self.logger.error(f"Perform error: {error}")
            self.logger.error(f"Service status: {result}")
            raise error

    def perform_ensure(self) -> None:
        self.logger.debug("perform_ensure")
        if not SYSTEM_CTL.has_unit(self.service_name()):
            self.perform_create()
        if not SYSTEM_CTL.has_enabled(self.service_name()):
            self.perform_enable()
        if not SYSTEM_CTL.has_active(self.service_name()):
            self.perform_with_status(self.perform_start)

    def perform_desure(self) -> None:
        self.logger.debug("perform_desure")
        if SYSTEM_CTL.has_active(self.service_name()):
            self.perform_with_status(self.perform_stop)
        if SYSTEM_CTL.has_enabled(self.service_name()):
            self.perform_disable()
        if SYSTEM_CTL.has_unit(self.service_name()):
            self.perform_delete()

    def perform_create(self) -> None:
        self.perform_command()
        self.logger.debug("perform_create")
        machine_result = machine_result_from_url(self.image_url, self.machine_meta)
        machine_result.profile_bucket.with_bucket(self.profile_bucket)
        perform_machine_create(machine_result)

    def perform_delete(self) -> None:
        self.logger.debug("perform_delete")
        machine_result = machine_result_from_url(self.image_url, self.machine_meta)
        perform_machine_delete(machine_result)

    def perform_enable(self) -> None:
        self.logger.debug("perform_enable")
        SYSTEM_CTL.enable(self.service_name()).assert_return()

    def perform_disable(self) -> None:
        self.logger.debug("perform_disable")
        SYSTEM_CTL.disable(self.service_name()).assert_return()

    def perform_start(self) -> None:
        self.logger.debug("perform_start")
        SYSTEM_CTL.start(self.service_name()).assert_return()

    def perform_stop(self) -> None:
        self.logger.debug("perform_stop")
        SYSTEM_CTL.stop(self.service_name()).assert_return()

    def perform_nsenter(self) -> None:
        self.logger.debug("perform_nsenter")
        NSENTER.execute_invoke(self.machine_name())

    def has_machine(self, present:bool=True) -> bool:
        from operator import xor
        expect = not present
        actual = MACHINE_CTL.has_machine(self.machine_name())
        return xor(expect, actual)

    def machine_await(self, present:bool=True, limit:int=5) -> None:
        count = 0
        while count < limit and not self.has_machine(present):
            time.sleep(1)
            count += 1

    @cached_method
    def mapper_action_perform(self) -> Mapping[str, Callable]:
        mapper = dict([
            (SetupAction.ensure.name, self.perform_ensure),
            (SetupAction.desure.name, self.perform_desure),
            (SetupAction.create.name, self.perform_create),
            (SetupAction.delete.name, self.perform_delete),
            (SetupAction.enable.name, self.perform_enable),
            (SetupAction.disable.name, self.perform_disable),
            (SetupAction.start.name, self.perform_start),
            (SetupAction.stop.name, self.perform_stop),
            (SetupAction.update.name, self.perform_update),
            (SetupAction.command.name, self.perform_command),
            (SetupAction.nsenter.name, self.perform_nsenter),
        ])
        return mapper

    @cached_method
    def mapper_effect_invoke(self) -> token.MappingEffectInvoke:
        mapper = dict([
            (token.ImageEffect, self.invoke_image),
            (token.MachineEffect, self.invoke_machine),
            (token.ProfileEffect, self.invoke_profile),
            (token.ExecEffect, self.invoke_exec),
            (token.CopyEffect, self.invoke_copy),
            (token.TemplateEffect, self.invoke_template),
            (token.RunEffect, self.invoke_run),
            (token.ShellEffect, self.invoke_shell),
        ])
        return mapper

    def perform_intent(self):

        self.logger.info("Performing setup")

        effect_list = self.effect_list()
        engine.verify_error(effect_list)

        config_mapper = map(self.invoke_effect, effect_list)

        engine.apply_visit(config_mapper)

        setup_action = self.parse_result.space.action
        perform_mapper = self.mapper_action_perform()

        self.logger.info(f"Setup service='{self.service_name()}' action='{setup_action}'")

        perform_function = perform_mapper[setup_action]
        perform_function()

        self.logger.info("Setup complete")


ENGINE = SetupEgine()

