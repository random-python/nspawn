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
service_user_file = service_config['service_user_file']

#
# perfrom build
#

IMAGE(image_url)

PULL(alpine_url)

WITH(
    Boot='yes',
    KillSignal="SIGUSR1",
)

# nginx storage folder
WITH(Bind=service_store_dir + '/')

# nginx web access credentials
WITH(BindReadOnly=service_user_file)

# system logging
WITH(Bind=f"{service_log_dir}:/var/log/")

# default config
COPY("/etc")
COPY("/root")

# configure host name
CAST("/etc/hostname",
    machine_name=machine_name,
)

# configure web server
CAST("/etc/nginx/conf.d/image.conf",
    service_store_dir=service_store_dir,
    service_user_file=service_user_file,
)

# basic system setup
SH("apk update")
SH("apk upgrade")
SH("apk add tzdata")
SH("apk add ca-certificates")
SH("apk add busybox-initscripts")
SH("apk add mc htop pwgen")
SH("apk add syslog-ng logrotate")
# SH("apk add iputils iproute2") # breaks some dependency
SH("apk add dhcpcd openssh")
SH("apk add nginx openssl")

# ensure system services
SH("rc-update add syslog-ng")
SH("rc-update add dhcpcd")
SH("rc-update add nginx")
SH("rc-update add crond")
SH("rc-update add sshd")

# web tls
SH("/etc/nginx/conf.d/image-tls.sh")

# container ssh access
SH("""
    echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config
    echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
    user=root; pass=$(pwgen -s 64 1); echo $user:$pass | chpasswd
""")

PUSH()
