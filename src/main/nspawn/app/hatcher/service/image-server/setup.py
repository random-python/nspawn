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
service_user_file = service_config['service_user_file']

user_file = service_config['service_user_file']
user_dir = os.path.dirname(user_file)
user_data = """
# nginx user login database
# http://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
default:{PLAIN}default
"""

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

WITH(BindReadOnly="/root/.ssh/authorized_keys")

# setup storage
SH(f"""
    mkdir -p "{service_home}"
    mkdir -p "{service_store_dir}"
    mkdir -p "{service_log_dir}"
    mkdir -p "{service_log_dir}/nginx"
    mkdir -p "{user_dir}"
    chmod -R o-rwx "{service_home}"
    chown -R {service_uid}:{service_gid} "{service_home}"
""")

# setup http access
SH(f"""
    if [ -s "{user_file}" ] ; then
        echo "Keeping exising user file: {user_file}"
    else
        echo "Writing default user file: {user_file}"
        echo "{user_data}" > "{user_file}"
    fi
""")
