#!/usr/bin/env python

from nspawn.setup import *

build_epoch = TOOL.build_epoch()
version_dash = TOOL.date_dash(build_epoch)

machine_name = "arch-http"
machine_home = f"/home/{machine_name}"

SH(f"""
    mkdir -p "{machine_home}"
    chown -R http:http "{machine_home}"
""")

network_face = TOOL.select_interface()

#
#
#

IMAGE(f"file://localhost/tmp/nspawn/repo/archlinux/http/{version_dash}.tar.gz")

MACHINE(machine_name)

WITH(
    MACVLAN=network_face,
)

bind_list = [
    (machine_home, '/home/'),
]

for source, target in bind_list:
    WITH(Bind=f"{source}:{target}")

WITH(Bind="/root/.ssh/authorized_keys")
