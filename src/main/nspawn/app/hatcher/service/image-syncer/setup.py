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
service_config = arkon['service_config']

machine_name = service_config['machine_name']
service_home = service_config['service_home']
service_store_dir = service_config['service_store_dir']

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

# remote machine access
WITH(BindReadOnly="/root/.ssh/authorized_keys")

# setup storage
SH(f"""
    mkdir -p "{service_home}"
    mkdir -p "{service_store_dir}"
""")

# verify storage
SH(f"""
    ls -las "{service_home}"
""")
