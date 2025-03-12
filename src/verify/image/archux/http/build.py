#!/usr/bin/env python

from nspawn.build import *

build_epoch = TOOL.build_epoch()
version_dash = TOOL.date_dash(build_epoch)

IMAGE(f"file://localhost/tmp/nspawn/repo/archux/http/{version_dash}.tar.gz")

PULL(f"file://localhost/tmp/nspawn/repo/archux/base/{version_dash}.tar.gz")

SH("pacman --sync --needed --noconfirm "
    "nginx "
)

SH("systemctl enable "
   "nginx.service "
)

COPY("/etc")
COPY("/opt")
COPY("/usr")

PUSH()
