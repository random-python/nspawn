#!/usr/bin/env python

# import os, runpy
# this_dir = os.path.dirname(os.path.abspath(__file__))
# runpy.run_path(f"{this_dir}/a.py")

from nspawn.build import *

import platform

epoch = "3.10"
release = f"{epoch}.3"
hardware = platform.machine()

# declare image identity
IMAGE(f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz")

# provision dependency image
PULL(f"http://dl-cdn.alpinelinux.org/alpine/v{epoch}/releases/{hardware}/alpine-minirootfs-{release}-{hardware}.tar.gz")

# alpine termination for /sbin/init (i.e. /bin/busybox)
WITH(KillSignal="SIGUSR1")

# provide environment varialbes
WITH(Environment='TEST_1=solid-value')
WITH(Environment='TEST_2=value with space')
WITH(Environment='TEST_3=value : with : colon')
WITH(Environment='TEST_4=value " with " double quote')

# download remote resources
# FETCH(url=f"http://aaa.bbb", path="/root/ssh")

# copy local resources
COPY("/etc")
COPY("/root")

# template local resources
CAST("/root/readme.md", variable="template varialbe")

SH("env|sort")
SH("ip addr")
SH("cat /etc/resolv.conf")
SH("ping -c 1 www.google.com")
# SH("ping -c 1 work1")
# SH("ping -c 1 work3")
# SH("ping -c 1 nspawn-proxy-server")

# download and extract remote resource
FETCH(
    url="https://github.com/random-python/nspawn/archive/master.zip",
    source="nspawn-master",
    target="/opt/nspawn",
)

# verify extract of remote resource
SH("ls -las /opt/nspawn")

# invoke program
RUN(["/usr/bin/env"])

# invoke shell script
SH("apk update")
SH("apk upgrade")
SH("apk add tzdata")
SH("apk add ca-certificates")
SH("apk add busybox-initscripts")
SH("apk add rsyslog")
SH("apk add mc htop pwgen")
SH("apk add iputils iproute2")
SH("apk add dhcpcd openssh ")

SH("rc-update add rsyslog")
SH("rc-update add dhcpcd")
SH("rc-update add sshd")

SH("""
    echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config
    echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
    user=root; pass=$(pwgen -s 64 1); echo $user:$pass | chpasswd
""")

# publish image
PUSH()
