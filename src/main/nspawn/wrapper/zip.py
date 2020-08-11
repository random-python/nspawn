from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo
from nspawn.support.process import execute_process_unit


class CmdZip(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/zip')

    def with_archive(self, path):
        self.with_option('xxx', path)
        return self

    def with_extract(self, path):
        self.with_option('xxx', path)
        return self

    def with_make_pack(self):
        return self

    def with_make_unpack(self):
        raise RuntimeError("wrong operation")


class CmdUnZip(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/unzip')

    def with_archive(self, path:str):
        assert path.endswith(".zip")
        self.option_list.extend([path])
        return self

    def with_extract(self, path:str):
        self.option_list.extend(['-d', path])
        return self

    def with_make_pack(self):
        raise RuntimeError("wrong operation")

    def with_make_unpack(self):
        return self

