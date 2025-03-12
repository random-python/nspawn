#!/usr/bin/env python

from nspawn.build import *

build_epoch = TOOL.build_epoch()
version_dash = TOOL.date_dash(build_epoch)

getmail_src = 'getmail-5.14'
getmail_dst = '/opt/getmail'
getmail_url = f"http://pyropus.ca/software/getmail/old-versions/{getmail_src}.tar.gz"

IMAGE(f"file://localhost/tmp/nspawn/repo/archux/mail/{version_dash}.tar.gz")

PULL(f"file://localhost/tmp/nspawn/repo/archux/base/{version_dash}.tar.gz")

SH("pacman --sync --needed --noconfirm "
    "python2 "
    "postfix "
)

COPY("/etc")

FETCH(url=getmail_url, source=getmail_src, target=getmail_dst)

SH(f"""
    cd {getmail_dst}
    python2 setup.py install
""")

PUSH()
