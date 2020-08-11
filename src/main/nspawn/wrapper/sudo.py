"""
Wrapper for sudo
https://linux.die.net/man/8/sudo
"""

import os
import shlex
from typing import List, Mapping

from nspawn import CONFIG
from nspawn.wrapper.base import Base
from nspawn.support.parser import parse_text2dict


class Sudo(Base):
    """
    Provide basic file system operations
    """

    def __init__(self):
        super().__init__('wrapper/sudo')

    def script(self, script:str) -> None:
        self.execute_unit_sert(script.split())

    def folder_check(self, path:str) -> bool:
        return self.has_success(['test', '-d', path])

    def folder_assert(self, path:str) -> None:
        assert self.folder_check(path), f"missing path '{path}'"

    def folder_ensure(self, path:str) -> None:
        self.execute_unit_sert(['mkdir', '--parents', path])

    def parent_ensure(self, path:str) -> None:
        folder = os.path.dirname(path)
        self.folder_ensure(folder)

    def file_check(self, path:str) -> bool:
        return self.has_success(['test', '-f', path])

    def file_assert(self, path:str):
        assert self.file_check(path), f"missing path '{path}'"

    def file_load(self, path) -> str:
        return self.execute_unit_sert(['cat', path]).stdout

    def file_save(self, path:str, text:str) -> None:
        self.parent_ensure(path)
        self.execute_unit_sert(['dd', f"of={path}"] , stdin=text)

    def files_copy(self, source:str, target:str) -> None:
        self.parent_ensure(target)
        self.execute_unit_sert(['cp', '--force', source, target])

    def files_move(self, source:str, target:str) -> None:
        self.files_delete(target)
        self.parent_ensure(target)
        self.execute_unit_sert(['mv', '--force', source, target])

    def files_delete(self, path:str) -> None:
        self.execute_unit_sert(['rm', '--force', '--recursive', path])
    #
    #
    #

    def files_sync_any(self, source:str, target:str, opts_line:str) -> None:
        "invoke rsync"
        if self.folder_check(source):
            source = os.path.join(source, '')  # ensure traling slash
            self.folder_ensure(target)
        else:
            self.parent_ensure(target)
        opts_list = shlex.split(opts_line)
        command = ['rsync'] + opts_list + [source, target ]
        self.execute_unit_sert(command)

    def files_sync_base(self, source:str, target:str) -> None:
        "options for DSL.COPY, DSL.CAST"
        rsync_base = CONFIG['wrapper/sudo']['rsync_base']
        self.files_sync_any(source, target, rsync_base)

    def files_sync_full(self, source:str, target:str) -> None:
        "options for DSL.PULL, DSL.PUSH"
        rsync_full = CONFIG['wrapper/sudo']['rsync_full']
        self.files_sync_any(source, target, rsync_full)

    def files_sync_time(self, source:str, target:str):
        "transfer file time only"
        self.execute_unit_sert(['touch', '-r', source, target])

    #
    # store file meta data in xattr
    #

    def xattr_space(self) -> str:
        "attribute name space used by this package"
        return CONFIG['wrapper/sudo']['xattr_space']

    def xattr_regex(self) -> str:
        "regular expression used to match package attributes"
        return CONFIG['wrapper/sudo']['xattr_regex']

    def xattr_name(self, key:str) -> str:
        "produce package-specific attribute name"
        return f"{self.xattr_space()}{key}"

    def xattr_get(self, path:str, key:str) -> str:
        "load single extendend path attribute"
        # -n name, --name=name    Dump the value of the named extended attribute
        # --only-values    Dump out the extended attribute value(s) only
        name = self.xattr_name(key)
        result = self.execute_unit(['getfattr', '-n', name, '--only-values', path])
        if result.rc == 0:
            return result.stdout
        else:
            return None

    def xattr_set(self, path:str, key:str, value:str) -> None:
        "save single extendend file attribute"
        # -n name, --name=name    Specifies the name of the extended attribute to set
        # -v value, --value=value    Specifies the new value of the extended attribute
        name = self.xattr_name(key)
        self.execute_unit_sert(['setfattr', '-n', name, '-v', value, path])

    def xattr_load(self, path:str) -> Mapping[str, str]:
        "retrieve extended file attributes as dictionary"
        # -d, --dump    Dump the values of all extended attributes
        # -m pattern, --match=pattern    Only include attributes with names matching the regular expression
        result = self.execute_unit(['getfattr', '-d', '-m', self.xattr_regex(), path])
        temp_dict = parse_text2dict(result.stdout)
        data_dict = dict()
        for name, data in temp_dict.items():  # deserialize
            key = name.replace(self.xattr_space(), '')
            value = data[1:-1]  # remove quotes
            data_dict[key] = value
        return data_dict

    def xattr_save(self, path:str, data_dict:Mapping[str, str]) -> None:
        "persist dictionary as extended file attributes"
        for key, value in data_dict.items():
            self.xattr_set(path, key, value)


SUDO = Sudo()
