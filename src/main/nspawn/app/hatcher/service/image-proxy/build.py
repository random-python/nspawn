#!/usr/bin/env python

"""
Service build script.
"""

from nspawn.build import *

# load shared config
import os
import runpy
this_dir = os.path.dirname(os.path.abspath(__file__))
arkon = runpy.run_path(f"{this_dir}/arkon.py")
image_url = arkon['image_url']
alpine_url = arkon['alpine_url']
service_config = arkon['service_config']

machine_name = service_config['machine_name']
service_gid = service_config['service_gid']
service_uid = service_config['service_uid']
service_home = service_config['service_home']
service_log_dir = service_config['service_log_dir']
service_store_dir = service_config['service_store_dir']

#
# perfrom build
#

IMAGE(image_url)

PULL(alpine_url)

WITH(
    Boot='yes',
    KillSignal="SIGUSR1",
)

# default config
COPY("/etc")
COPY("/root")

# configure host name
CAST("/etc/hostname",
    machine_name=machine_name,
)

# configure proxy server
# CAST("/etc/nginx/conf.d/image.conf",
#     service_store_dir=service_store_dir,
#     service_user_file=service_user_file,
# )

# basic system setup
SH("apk update")
SH("apk upgrade")
SH("apk add tzdata")
SH("apk add ca-certificates")
SH("apk add busybox-initscripts")
SH("apk add mc htop pwgen")
SH("apk add syslog-ng logrotate")
# SH("apk add iputils iproute2")
SH("apk add dhcpcd openssh")
SH("apk add squid openssl")

# ensure system services
SH("rc-update add syslog-ng")
SH("rc-update add dhcpcd")
SH("rc-update add squid")
SH("rc-update add sshd")

# store_id_program
SH("apk add python3")

# container ssh access
SH("""
    echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config
    echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
    user=root; pass=$(pwgen -s 64 1); echo $user:$pass | chpasswd
""")

# configure squid
SH("""
    chmod +x /etc/squid/*.py
    /usr/lib/squid/security_file_certgen -c -s /etc/squid/crtd -M 4MB
    chown -R squid:squid /etc/squid/crtd
""")

PUSH()
