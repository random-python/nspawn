
from nspawn.wrapper.sudo import SUDO
from nspawn.support.files import make_temp_path
from nspawn.packer.base import Provider
from typing import List
from nspawn.wrapper.zip import CmdZip
from nspawn.wrapper.zip import CmdUnZip


class ProviderZip(Provider):

    @classmethod
    def suffix_list(cls) -> List[str]:
        return ['.zip']

    def archive(self, archive_path:str, extract_path:str) -> None:
        SUDO.folder_assert(extract_path)
        archive_temp = make_temp_path("zip-archive-temp")
        SUDO.parent_ensure(archive_temp)
        zipper = CmdZip()
        zipper.with_archive(archive_temp)
        zipper.with_extract(extract_path)
        zipper.execute_unit_sert()
        SUDO.files_move(archive_temp, archive_path)

    def extract(self, archive_path:str, extract_path:str) -> None:
        SUDO.file_assert(archive_path)
        extract_temp = make_temp_path("zip-extract-temp")
        SUDO.folder_ensure(extract_temp)
        zipper = CmdUnZip()
        zipper.with_archive(archive_path)
        zipper.with_extract(extract_temp)
        zipper.execute_unit_sert()
        SUDO.files_move(extract_temp, extract_path)
