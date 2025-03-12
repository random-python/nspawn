#!/usr/bin/env python

# import os, runpy
# this_dir = os.path.dirname(os.path.abspath(__file__))
# runpy.run_path(f"{this_dir}/a.py")

from nspawn.setup import *

import platform

epoch = "3.10"
release = f"{epoch}.3"
hardware = platform.machine()

machine_name = "alpa-base"
network_face = TOOL.select_interface()

IMAGE(f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz")

MACHINE(
    # define machine name
    name=machine_name,
    # extra entries for [Unit] section
    unit_conf=[
        "Description=hello-kitty",  # override description
    ],
    # extra entries for [Service] section
    service_conf=[
        "CPUQuota=10%",  # throttle processor usage
    ],
    # extra entries for [Install] section
    install_conf=[
        "# user comment: hello-kitty",  # inject user comment
    ],
)

WITH(
#     Hostname="alpase", # needs systemd v 239
    Boot='yes',  # auto detect /bin/init program
    Quiet="yes",  # suppress "press to escape" message
    KeepUnit="yes",  # use service unit as nspawn scope
    Register="yes",  # expose service unit with machinectl
    MACVLAN=network_face,
#     Capability='all',
)

# use host ssh login for container
WITH(BindReadOnly="/root/.ssh/authorized_keys")

# alpine system entry
# EXEC(['/sbin/init'])
# EXEC(['/bin/ls', '-Rlas', f"/root"])

# external config
config_dir = f"{TOOL.nspawn_tempdir()}/machine/{machine_name}"

# externally configurable hostname
hostname_path = f"{config_dir}/etc/hostname"
WITH(BindReadOnly=f"{hostname_path}:/etc/hostname")
CAST(source="/etc/hostname", target=hostname_path, machine_name=machine_name)

# externally exposed message log
messages_path = f"{config_dir}/var/log/messages"
WITH(Bind=f"{messages_path}:/var/log/messages")
