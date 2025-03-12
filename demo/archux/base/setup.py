#!/usr/bin/env python

# activate setup dsl
from nspawn.setup import *

# define image url
version_path = "2019/06/01"
version_dots = "2019.06.01"
version_dash = "2019-06-01"
archux_url = "https://archive.archlinux.org"
booter_url = f"{archux_url}/iso/{version_dots}/archlinux-bootstrap-{version_dots}-x86_64.tar.gz"
mirror_url = f"{archux_url}/repos/{version_path}/$repo/os/$arch"

# discover network interface
network_face = TOOL.select_interface()

# declare machine image
IMAGE(url=f"file://localhost/tmp/nspawn/repo/archlinux/base/{version_dash}.tar.gz")

# provide machine identity
MACHINE(name=f"archux-base") # sets default hostname

# customize machine service
WITH(
#     Hostname="archlinux-base", # needs systemd v 239
    MACVLAN=network_face,  # create a "macvlan" interface of the specified network interface and add it to the container
)

# configure machine ssh access
WITH(BindReadOnly="/root/.ssh/authorized_keys")
