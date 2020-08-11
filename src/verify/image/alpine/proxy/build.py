#!/usr/bin/env python

from nspawn.build import *

import platform

epoch = "3.10"
release = f"{epoch}.3"
hardware = platform.machine()

# declare image identity
IMAGE(f"file://localhost/tmp/nspawn/repo/alpine/proxy/default-{release}-{hardware}.tar.gz")

# provision dependency image
PULL(f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz")

# invoke shell script
SH("apk add squid")
SH("rc-update add squid")

# publish image
PUSH()
