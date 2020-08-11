#!/usr/bin/env python

# activate build dsl
from nspawn.build import *

# define image url
version_path = "2019/11/01"
version_dots = "2019.11.01"
version_dash = "2019-11-01"
archux_url = "https://archive.archlinux.org"
booter_url = f"{archux_url}/iso/{version_dots}/archlinux-bootstrap-{version_dots}-x86_64.tar.gz"
mirror_url = f"{archux_url}/repos/{version_path}/$repo/os/$arch"

# declare image identity
IMAGE(url=f"file://localhost/tmp/nspawn/repo/archlinux/base/{version_dash}.tar.gz")

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

# template local resources
CAST(path="/etc/pacman.d/mirrorlist", mirror_url=mirror_url)

SH(script="pacman-key --init")
SH(script="pacman-key --populate")
SH(script="pacman --sync --needed --noconfirm --refresh")
SH(script="pacman --sync --needed --noconfirm mc htop")
SH(script="pacman --sync --needed --noconfirm iputils iproute2")
SH(script="pacman --sync --needed --noconfirm openssh")
SH(script="systemctl enable systemd-networkd")
SH(script="systemctl enable systemd-resolved")
SH(script="systemctl enable sshd")

# publish image
PUSH()
