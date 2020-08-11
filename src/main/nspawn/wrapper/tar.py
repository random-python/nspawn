"""
Wrapper for tar
https://linux.die.net/man/1/tar
"""

from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo
from nspawn.support.process import execute_process_unit


def compressor_for(file:str) -> str:
    if file.endswith('.tar.gz'):
        return 'pigz'
    if file.endswith('.tar.xz'):
        return 'xz'
    else:
        raise RuntimeError(f"Missing compressor for {file}")


class Tar(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/tar')

    def with_archive(self, path):
        self.with_option('file', path)
        return self

    def with_extract(self, path):
        self.with_option('directory', path)
        return self

    def with_compress(self, path):
        self.with_option('use-compress-program', path)
        return self

    def with_make_pack(self):
        self.with_option('create', '.')
        return self

    def with_make_unpack(self):
        self.with_option('extract')
        return self

    def with_packer(self, file):
        self.with_compress(compressor_for(file))
        return self

