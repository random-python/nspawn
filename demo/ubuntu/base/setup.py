#!/usr/bin/env python

# activate setup dsl
from nspawn.setup import *

# define image url
name = "bionic"
version = "18.04"
image_url = f"file://localhost/tmp/nspawn/repo/ubuntu/base/{name}-{version}.tar.gz"
booter_url = f"https://cloud-images.ubuntu.com/minimal/releases/{name}/release/ubuntu-{version}-minimal-cloudimg-amd64-root.tar.xz"

# discover network interface
network_face = TOOL.select_interface()

# declare image identity
IMAGE(image_url)

# provide machine identity
MACHINE(name=f"ubuntu-base") # sets default hostname

WITH(
#     Hostname="ubuntase", # needs systemd v 239
    MACVLAN=network_face,
)

# configure machine ssh access
WITH(BindReadOnly="/root/.ssh/authorized_keys")
