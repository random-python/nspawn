
from nspawn.packer.base import *


def test_packer_provider():
    archive_list = [
        'http://host/path/archux_url.tar.gz',
    ]
    for archux_url in archive_list:
        provider = packer_provider(archux_url)
        print(provider)
