#!/usr/bin/env python

"""
Service setup script.
"""

from nspawn.setup import *

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

service_etc = f"{service_home}/etc"
service_etc_tmp = f"{service_home}/etc_tmp"

# discover host network
network_face = TOOL.select_interface()

#
# perform setup
#

IMAGE(image_url)

MACHINE(machine_name)

WITH(
    Quiet="yes",
    KeepUnit="yes",
    Register="yes",
    MACVLAN=network_face,
)

# admin access
WITH(BindReadOnly="/root/.ssh/authorized_keys")

# system logging
WITH(Bind=f"{service_log_dir}:/var/log/")

# storage folder
WITH(Bind=f"{service_store_dir}:/var/cache/squid/")

# expose settings
WITH(Overlay=f"+/etc:{service_etc}:{service_etc_tmp}:/etc")

# setup permissions
SH(f"""
    mkdir -p "{service_home}"
    mkdir -p "{service_store_dir}"
    mkdir -p "{service_log_dir}/squid"
    chmod -R o-rwx "{service_home}"
    chown -R {service_uid}:{service_gid} "{service_home}"
""")
