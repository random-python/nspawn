#!/usr/bin/env python

from nspawn.setup import *

build_epoch = TOOL.build_epoch()
version_dash = TOOL.date_dash(build_epoch)

network_face = TOOL.select_interface()

IMAGE(url=f"file://localhost/tmp/nspawn/repo/archux/base/{version_dash}.tar.gz")

MACHINE(name=f"arch-base")

WITH(
#     Hostname="archase", # needs systemd v 239
    MACVLAN=network_face,
)

WITH(Bind=f"/root/.ssh/authorized_keys")
