#!/usr/bin/env python

# activate setup dsl
from nspawn.setup import *

# define image url
import platform
epoch = "3.9"
release = f"{epoch}.4"
hardware = platform.machine()
image_url = f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz"

# discover network interface
network_face = TOOL.select_interface()

# declare machine image
IMAGE(url=image_url)

# provide machine identity
MACHINE(name="alpine-base") # sets default hostname

# customize machine service
WITH(
#     Hostname="alpase", # needs systemd v 239
    Boot="yes",  # locate /bin/init automatically
    Quiet="yes",  # suppress "press to escape" message
    KeepUnit="yes",  # use service unit as nspawn scope
    Register="yes",  # expose service unit with machinectl
    MACVLAN=network_face,  # create a "macvlan" interface of the specified network interface and add it to the container
)

# configure machine ssh access
WITH(BindReadOnly="/root/.ssh/authorized_keys")
