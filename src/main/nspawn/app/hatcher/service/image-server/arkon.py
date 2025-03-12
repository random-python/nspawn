"""
Service shared config.
"""

import platform
from nspawn import CONFIG

epoch = "3.11"
release = f"{epoch}.3"
hardware = platform.machine()

provision = CONFIG['storage']['provision']
image_url = f"file://localhost/{provision}/alpine/image-server/default-{release}-{hardware}.tar.gz"
alpine_url = f"http://dl-cdn.alpinelinux.org/alpine/v{epoch}/releases/{hardware}/alpine-minirootfs-{release}-{hardware}.tar.gz"
service_config = CONFIG['hatcher/image-server']
