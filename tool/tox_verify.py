#!/usr/bin/env python

"""
CI tox integration tests
"""

from devrepo import shell

shell(f"nspawn-hatch list")
shell(f"nspawn-hatch update image-server")
shell(f"cat /etc/systemd/system/nspawn-image-server.service")
shell(f"systemctl --no-pager status nspawn-image-server.service")

shell(f"nspawn-enter nspawn-image-server 'uname -a'")

shell(f"demo/alpine/base/build.py")
shell(f"demo/alpine/base/setup.py")
shell(f"cat /etc/systemd/system/alpine-base.service")
shell(f"systemctl --no-pager status alpine-base.service")

# TODO archux site is slow
# shell(f"demo/archux/base/build.py")
# shell(f"demo/archux/base/setup.py")
# shell(f"cat /etc/systemd/system/archux-base.service")
# shell(f"systemctl --no-pager status archux-base.service")

shell(f"demo/ubuntu/base/build.py")
shell(f"demo/ubuntu/base/setup.py")
shell(f"cat /etc/systemd/system/ubuntu-base.service")
shell(f"systemctl --no-pager status ubuntu-base.service")

shell(f"machinectl --no-pager")

shell(f"nspawn-hatch desure image-server")
shell(f"demo/alpine/base/setup.py --action=desure")
shell(f"demo/archux/base/setup.py --action=desure")
shell(f"demo/ubuntu/base/setup.py --action=desure")

shell(f"machinectl --no-pager")
