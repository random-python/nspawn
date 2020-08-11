#!/usr/bin/env python

from nspawn.build import *

import platform

epoch = "3.10"
release = f"{epoch}.3"
hardware = platform.machine()

# declare image identity
IMAGE(f"file://localhost/tmp/nspawn/repo/alpine/mail/default-{release}-{hardware}.tar.gz")

# provision dependency image
PULL(f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz")

# invoke shell script
SH("apk add postfix")
SH("rc-update add postfix")

# publish image
PUSH()
