"""
Container profile representation.

Provides profile entires as both nspawn settings and nspawn options.

Nspawn Settings:
    https://www.freedesktop.org/software/systemd/man/systemd.nspawn.html

Nspawn Options:
    https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
"""

import functools
from functools import partial
from dataclasses import dataclass, field, replace
from typing import Any, List, Callable, Type, Mapping
from nspawn.wrapper.base import Command
from nspawn.support.typing import cached_method, WithTypeNameTrait
from builtins import isinstance

frozen = dataclass(frozen=True)


@frozen
class AnyType():
    """
    Base class for settings section type.
    """


@frozen
class ExecType(AnyType):
    """
    Profile options in [Exec] settings section.
    """


@frozen
class FilesType(AnyType):
    """
    Profile options in [Files] settings section.
    """


@frozen
class NetworkType(AnyType):
    """
    Profile options in [Network] settings section.
    """


@frozen
class BuildType(AnyType):
    """
    Profile options appplied during build.
    """


@frozen
class CommandType(AnyType):
    """
    Profile options present only in command line and missing as settings.
    """

#
#
#


@frozen
class AnyEntry(WithTypeNameTrait, object):
    """
    Base type for profile settings/options.

    Convention:
    Type name matches settings name of systemd.nspawn:
        token format: 'SettingName=token-value'
        https://www.freedesktop.org/software/systemd/man/systemd.nspawn.html
    Option name matches options name of systemd-nspawn:
        token format: '--option-name=token-value'
        https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html

    Attributes:
        origin: image which contributed this entry
        version: minimal supported version of systemd
        use_key_only: indicates that entry takes no value
        option: entry representation on command line
        value: settings/options value
    """
    # payload
    value:str = field()
    # meta info
    origin:str = field(init=True, default=None, repr=False)
    option:str = field(init=False)
    version:int = field(init=False, default=0, repr=False)
    use_key_only:bool = field(init=False, default=False, repr=False)

    def quoted_value(self, quote=""):
        return f'{quote}{self.value}{quote}'

    def render_entry(self, quote=""):
        return f'{self.type_name()}={self.quoted_value(quote)}'

    def render_option(self, quote=""):
        if self.use_key_only:
            return self.render_empty_option(quote)
        else:
            return self.render_value_option(quote)

    def render_empty_option(self, quote=""):
        if self.value.lower() in ("yes", "on", "true"):
            return f'{self.option}'
        else:
            return None

    def render_value_option(self, quote=""):
        return f'{self.option}={self.quoted_value(quote)}'


class BindPathTrait():
    """
    Parse Bind("host_path:container_path") values
    """

    def host_path(self) -> str:
        if ':' in self.value:
            return self.value.split(':')[0]
        else:
            return self.value

    def container_path(self) -> str:
        if ':' in self.value:
            return self.value.split(':')[1]
        else:
            return self.value

    def has_folder(self) -> bool:
        return self.has_host_folder() or self.has_container_folder()

    def has_host_folder(self) -> bool:
        return self.host_path().endswith('/')

    def has_container_folder(self) -> bool:
        return self.container_path().endswith('/')


class OverlayPathTrait():
    """
    Parse Overlay("lower:upper:mount") values
    """

    def path_list(self) -> List[str]:
        term_list = self.value.split(':')
        if len(term_list) < 2:
            raise RuntimeError(f"Invalid overlay: '{self.value}'")
        if len(term_list) == 2:
            # reify container mount
            term_list = term_list + [term_list[-1]]
        assert len(term_list) >= 3
        return term_list

    def host_path_list(self) -> List[str]:
        # drop last, i.e. container mount
        path_list = self.path_list()[:-1]
        # drop auto-temp and container-relative folders
        select = lambda term : term and not term.startswith('+')
        return list(filter(select, path_list))

    def container_path(self) -> str:
        return self.path_list()[-1]


class ProfileEntry():
    """
    Collection of recognized profile settings/options.
    """

    #
    # Special Section - comman line only
    #

    @frozen
    class Quiet(AnyEntry, CommandType):
        option = "--quiet"
        use_key_only = True
        version = 209

    @frozen
    class KeepUnit(AnyEntry, CommandType):
        option = "--keep-unit"
        use_key_only = True
        version = 209

    @frozen
    class Register(AnyEntry, CommandType):
        option = "--register"
        version = 209

    @frozen
    class Property(AnyEntry, CommandType):
        option = "--property"
        version = 220

    @frozen
    class Slice(AnyEntry, CommandType):
        option = "--slice"

    @frozen
    class Console(AnyEntry, CommandType):
        option = "--console"
        version = 242

    @frozen
    class AutoPrivateUsers(AnyEntry, CommandType):
        option = "-U"
        version = 230

    #
    # [Exec] Section in machine.nspawn
    #

    @frozen
    class Boot(AnyEntry, ExecType):
        option = "--boot"
        use_key_only = True

    @frozen
    class Ephemeral(AnyEntry, ExecType):
        option = "--ephemeral"
        use_key_only = True

    @frozen
    class ProcessTwo(AnyEntry, ExecType):
        option = "--as-pid2"
        use_key_only = True

    @frozen
    class Parameters(AnyEntry, ExecType):
        option = "<invalid>"

        def render_option(self):
            raise RuntimeError("TODO")

    @frozen
    class Environment(AnyEntry, ExecType, BuildType):
        option = "--setenv"
        version = 209

    @frozen
    class User(AnyEntry, ExecType):
        option = "--user"

    @frozen
    class WorkingDirectory(AnyEntry, ExecType, BuildType):
        option = "--chdir"

    @frozen
    class PivotRoot(AnyEntry, ExecType):
        option = "--pivot-root"

    @frozen
    class Capability(AnyEntry, ExecType):
        option = "--capability"
        version = 186

    @frozen
    class DropCapability(AnyEntry, ExecType):
        option = "--drop-capability"
        version = 209

    @frozen
    class NoNewPrivileges(AnyEntry, ExecType):
        option = "--no-new-privileges"
        version = 239

    @frozen
    class KillSignal(AnyEntry, ExecType):
        option = "--kill-signal"

    @frozen
    class Personality(AnyEntry, ExecType):
        option = "--personality"
        version = 209

    @frozen
    class MachineID(AnyEntry, ExecType):
        option = "--uuid"

    @frozen
    class NotifyReady(AnyEntry, ExecType):
        option = "--notify-ready"
        version = 231

    @frozen
    class SystemCallFilter(AnyEntry, ExecType):
        option = "--system-call-filter"
        version = 235

    @frozen
    class Limit(AnyEntry, ExecType):
        option = "--rlimit"
        version = 239

    @frozen
    class OOMScoreAdjust(AnyEntry, ExecType):
        option = "--oom-score-adjust"
        version = 239

    @frozen
    class CPUAffinity(AnyEntry, ExecType):
        option = "--cpu-affinity"
        version = 239

    @frozen
    class Hostname(AnyEntry, ExecType):
        option = "--hostname"
        version = 239

    @frozen
    class ResolvConf(AnyEntry, ExecType):
        option = "--resolv-conf"
        version = 239

    @frozen
    class Timezone(AnyEntry, ExecType):
        option = "--timezone"
        version = 239

    @frozen
    class LinkJournal(AnyEntry, ExecType):
        option = "--link-journal"
        version = 218

    @frozen
    class PrivateUsers(AnyEntry, ExecType):
        option = "--private-users"
        version = 230

    #
    # [Files] Section in machine.nspawn
    #

    @frozen
    class ReadOnly(AnyEntry, FilesType):
        option = "--read-only"
        use_key_only = True

    @frozen
    class Volatile(AnyEntry, FilesType):
        option = "--volatile"
        version = 242

    @frozen
    class Bind(AnyEntry, FilesType, BindPathTrait):
        option = "--bind"

    @frozen
    class BindReadOnly(AnyEntry, FilesType, BindPathTrait):
        option = "--bind-ro"

    @frozen
    class TemporaryFileSystem(AnyEntry, FilesType):
        option = "--tmpfs"

    @frozen
    class Inaccessible(AnyEntry, FilesType):
        option = "--inaccessible"
        version = 242

    @frozen
    class Overlay(AnyEntry, FilesType, OverlayPathTrait):
        option = "--overlay"
        # version = 233 # "+" support
        version = 220

    @frozen
    class OverlayReadOnly(AnyEntry, FilesType, OverlayPathTrait):
        option = "--overlay-ro"
        # version = 233 # "+" support
        version = 220

    @frozen
    class PrivateUsersChown(AnyEntry, FilesType):
        option = "--private-users-chown"
        version = 230

    #
    # [Network] Section in machine.nspawn
    #

    @frozen
    class Private(AnyEntry, NetworkType):
        option = "--private-network"
        use_key_only = True

    @frozen
    class VirtualEthernet(AnyEntry, NetworkType):
        option = "--network-veth"
        use_key_only = True
        version = 209

    @frozen
    class VirtualEthernetExtra(AnyEntry, NetworkType):
        option = "--network-veth-extra"

    @frozen
    class Interface(AnyEntry, NetworkType):
        option = "--network-interface"
        version = 209

    @frozen
    class MACVLAN(AnyEntry, NetworkType):
        option = "--network-macvlan"

    @frozen
    class IPVLAN(AnyEntry, NetworkType):
        option = "--network-ipvlan"

    @frozen
    class Bridge(AnyEntry, NetworkType):
        option = "--network-bridge"
        version = 209

    @frozen
    class Zone(AnyEntry, NetworkType):
        option = "--network-zone"

    @frozen
    class Port(AnyEntry, NetworkType):
        option = "--port"


def has_public_name(name:str) -> bool:
    """Select public member name"""
    return not name.startswith('_') and not name.endswith('_')


@functools.lru_cache(maxsize=1)
def profile_entry_list() -> List[str]:
    """Extract names of settings"""
    attr_list = dir(ProfileEntry)
    selector = filter(has_public_name, attr_list)
    return list(selector)


@functools.lru_cache(maxsize=1)
def profile_option_list() -> List[str]:
    """Extract names of options"""
    mapper = profile_option_mapper()
    return list(mapper.keys())


@functools.lru_cache(maxsize=1)
def profile_option_mapper() -> Mapping[str, AnyEntry]:
    """Map from option name into entry class"""
    option_mapper = dict()
    entry_list = profile_entry_list()
    for entry in entry_list:
        entry_class = getattr(ProfileEntry, entry)
        entry_instance = entry_class('')
        option = entry_instance.option
        option_mapper[option] = entry_class
    return option_mapper


def parse_entry_list(entry_token_list:List[str]) -> List[AnyEntry]:
    """Deserialize setting list"""
    return list(map(lambda entry_token: parse_profile_entry(entry_token), entry_token_list))


def parse_profile_entry(entry_token:str, origin:str=None) -> AnyEntry:
    """Deserialize setting from 'key=value' token"""
    if '=' in entry_token:
        term_list = entry_token.split('=', 1)
        entry = term_list[0]
        value = term_list[1]
        return produce_profile_entry(entry, value, origin)
    else:
        raise SyntaxError(f"Expecting key=value: {entry_token}")


def produce_profile_entry(entry:str, value:str, origin:str=None) -> AnyEntry:
    """Instantiate setting by name"""
    if hasattr(ProfileEntry, entry):
        entry_class = getattr(ProfileEntry, entry)
        return entry_class(value=value, origin=origin)
    else:
        raise TypeError(f"Invalid entry: '{entry}'. Supported list: {profile_entry_list()}")


def parse_option_list(option_token_list:List[str]) -> List[AnyEntry]:
    """Deserialize option list"""
    return list(map(lambda option_token: parse_profile_option(option_token), option_token_list))


def parse_profile_option(option_token:str, origin:str=None) -> AnyEntry:
    """Deserialize option from '--key=value' token"""
    assert isinstance(option_token, str), f"need option_token string: {option_token}"
    if '=' in option_token:
        term_list = option_token.split('=', 1)
        option = term_list[0]
        value = term_list[1]
    else:
        option = option_token
        value = 'yes'
    return produce_profile_option(option, value, origin)


def produce_profile_option(option:str, value:str, origin:str=None) -> AnyEntry:
    """Instantiate option by name"""
    assert isinstance(option, str), f"need option string: {option}"
    assert isinstance(value, str), f"need value string: {option}"
    option_mapper = profile_option_mapper()
    if option in option_mapper:
        entry_class = option_mapper[option]
        return entry_class(value=value, origin=origin)
    else:
        raise TypeError(f"Invalid option: '{option}'. Supported list: {profile_option_list()}")


def selected_entry_list(select:Callable, entry_list:List[AnyEntry]) -> List[AnyEntry]:
    """Filter settings with predicate"""
    return list(filter(select, entry_list))


def host_bind_entry_list(entry_list:List[AnyEntry]) -> List[AnyEntry]:
    select = lambda entry: isinstance(entry, BindPathTrait)
    return selected_entry_list(select, entry_list)


def host_overlay_entry_list(entry_list:List[AnyEntry]) -> List[AnyEntry]:
    select = lambda entry: isinstance(entry, OverlayPathTrait)
    return selected_entry_list(select, entry_list)


def supported_entry_list(systemd_version:int, entry_list:List[AnyEntry]) -> List[AnyEntry]:
    select = lambda entry: entry.version <= systemd_version
    return selected_entry_list(select, entry_list)


def unsupported_entry_list(systemd_version:int, entry_list:List[AnyEntry]) -> List[AnyEntry]:
    select = lambda entry: entry.version > systemd_version
    return selected_entry_list(select, entry_list)


select_default:Callable = lambda entry: isinstance(entry, AnyType)


def render_any_list(
        entry_list:List[AnyEntry],
        render:Callable,
        select:Callable=select_default,
    ) -> List[str]:
    selector = filter(select, entry_list)
    renderer = map(render, selector)
    cleaner = filter(None, renderer)
    return list(cleaner)


def render_entry_list(
        entry_list:List[AnyEntry],
        quote="",
        select:Callable=select_default,
    ) -> List[str]:
    render = partial(AnyEntry.render_entry, quote=quote)
    return render_any_list(entry_list, render, select)


def render_option_list(
        entry_list:List[AnyEntry],
        quote="",
        select:Callable=select_default,
    ) -> List[str]:
    render = partial(AnyEntry.render_option, quote=quote)
    return render_any_list(entry_list, render, select)


@frozen
class ProfileBucket:
    """
    Represent systemd-nspawn command and options.
    """
    origin:str = field(default=None)
    command:List[str] = field(default=None)
    entry_list:List[AnyEntry] = field(default_factory=list)

    def with_command(self, command:List[str]):
        object.__setattr__(self, "command", command)
        return self

    def with_append_entry(self, name:str, value:str, origin:str=None):
        source = origin if origin else self.origin
        entry = produce_profile_entry(name, value, source)
        self.entry_list.append(entry)
        return self

    def with_append_option(self, name:str, value:str, origin:str=None):
        source = origin if origin else self.origin
        entry = produce_profile_option(name, value, source)
        self.entry_list.append(entry)
        return self

    def with_bucket(self, profile_bucket):
        self.with_command(profile_bucket.command)
        self.with_bucket_entry_list(profile_bucket)
        return self

    def with_bucket_command(self, profile_bucket):
        self.with_command(profile_bucket.command)
        return self

    def with_bucket_entry_list(self, profile_bucket):
        source_list:List[AnyEntry] = profile_bucket.entry_list
        target_list:List[AnyEntry] = []
        for source in source_list:
            if source.origin:
                target = source
            else:
                target = replace(source, origin=self.origin)
            target_list.append(target)
        self.entry_list.extend(target_list)
        return self

    def render_entry_list(self,
            quote="",
            select:Callable=select_default,
        ) -> List[str]:
        return render_entry_list(self.entry_list, quote, select)

    def render_option_list(self,
            quote="",
            select:Callable=select_default,
        ) -> List[str]:
        return render_option_list(self.entry_list, quote, select)


@frozen
class PartitionBucket:
    """
    Represent supported vs unsupported settings collection.
    """

    version: int
    entry_list: List[AnyEntry]

    @cached_method
    def supported_list(self) -> List[AnyEntry]:
        return supported_entry_list(self.version, self.entry_list)

    @cached_method
    def unsupported_list(self) -> List[AnyEntry]:
        return unsupported_entry_list(self.version, self.entry_list)

    def has_entry(self):
        return len(self.entry_list) > 0

    def has_supported(self):
        return len(self.supported_list()) > 0

    def has_unsupported(self):
        return len(self.unsupported_list()) > 0

    @classmethod
    def parse_entry_list(cls, version:int, entry_token_list:List[str]):
        entry_list = parse_entry_list(entry_token_list)
        return cls(version, entry_list)

    @classmethod
    def parse_option_list(cls, version:int, option_token_list:List[str]):
        entry_list = parse_option_list(option_token_list)
        return cls(version, entry_list)
