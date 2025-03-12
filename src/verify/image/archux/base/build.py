#!/usr/bin/env python

from nspawn.build import *

build_epoch = TOOL.build_epoch()
version_path = TOOL.date_path(build_epoch)
version_dots = TOOL.date_dots(build_epoch)
version_dash = TOOL.date_dash(build_epoch)

archux_url = "https://archive.archlinux.org"
booter_url = f"{archux_url}/iso/{version_dots}/archlinux-bootstrap-{version_dots}-x86_64.tar.gz"
mirror_url = f"{archux_url}/repos/{version_path}/$repo/os/$arch"

# declare image identity
IMAGE(url=f"file://localhost/tmp/nspawn/repo/archux/base/{version_dash}.tar.gz")

# provision dependency image
PULL(url=booter_url)

# configure container profile
WITH(
    Boot="yes",  # auto-find image init program
    Quiet="yes",  # suppress "press to escape" message
    KeepUnit="yes",  # use service unit as nspawn scope
    Register="yes",  # expose service unit with machinectl
)

# copy local resources
COPY(path="/etc")
COPY(path="/root")

# template local resources
CAST(path="/etc/pacman.d/mirrorlist", mirror_url=mirror_url)

# activate proxy tls
SH("update-ca-trust")

# ensure gpg keys
SH(script="pacman-key --init")
SH(script="pacman-key --populate")

# update package repository
SH(script="pacman --sync --needed --noconfirm --refresh")

# update database
SH("pacman --sync --refresh")

# install packages
SH("pacman --sync --needed --noconfirm "
   "mc htop file "
   "iputils iproute2 "
   "openssh "
)

# enable services
SH("systemctl enable "
   "systemd-networkd "
   "systemd-resolved "
   "sshd "
)

# publish image
PUSH()
