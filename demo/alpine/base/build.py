#!/usr/bin/env python

# activate build dsl
from nspawn.build import *

# define image url
import platform
epoch = "3.9"
release = f"{epoch}.4"
hardware = platform.machine()
image_url = f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz"
alpine_url = f"http://dl-cdn.alpinelinux.org/alpine/v{epoch}/releases/{hardware}/alpine-minirootfs-{release}-{hardware}.tar.gz"

# declare image identity
IMAGE(image_url)

# provision dependency image
PULL(alpine_url)

# termination for alpine /sbin/init (i.e. /bin/busybox)
WITH(KillSignal="SIGUSR1")

# copy local resources
COPY("/etc")
COPY("/root")

# template local resources
CAST("/root/readme.md", variable="template varialbe")

# invoke some bild program
RUN(["/usr/bin/env"])

# invoke build shell script
SH("apk update")
SH("apk upgrade")
SH("apk add tzdata")
SH("apk add ca-certificates")
SH("apk add busybox-initscripts")
SH("apk add mc htop pwgen")
SH("apk add iputils iproute2")
SH("apk add dhcpcd openssh ")
SH("rc-update add syslog")
SH("rc-update add dhcpcd")
SH("rc-update add sshd")
SH("""
    echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config
    echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
    user=root; pass=$(pwgen 64 1); echo $user:$pass | chpasswd
""")

# publish image to image url
PUSH()
