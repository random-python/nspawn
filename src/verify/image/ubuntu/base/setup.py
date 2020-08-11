#!/usr/bin/env python

import os, runpy
this_dir = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(f"{this_dir}/a.py")

from nspawn.setup import *

name = "bionic"
version = "18.04"
image_url = f"file://localhost/tmp/nspawn/repo/ubuntu/base/{name}-{version}.tar.gz"
booter_url = f"https://cloud-images.ubuntu.com/minimal/releases/{name}/release/ubuntu-{version}-minimal-cloudimg-amd64-root.tar.xz"

network_face = TOOL.select_interface()

# declare image identity
IMAGE(image_url)

MACHINE(name=f"ubun-base")

WITH(
#     Hostname="ubunase", # needs systemd v 239
    MACVLAN=network_face,
)
