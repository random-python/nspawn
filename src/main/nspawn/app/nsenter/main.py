"""
NSenter application entry.
"""

import sys

from nspawn.app.nsenter.parser import nsenter_parser
from nspawn.wrapper.systemctl import SYSTEM_CTL
from nspawn.wrapper.nsenter import NSENTER


def main():

    parser = nsenter_parser()
    space = parser.parse_args()

    machine = space.machine
    script = space.script

    service = f"{machine}.service"

    if not SYSTEM_CTL.has_active(service):
        sys.exit(f"Service is not active: {service}")

    if not SYSTEM_CTL.has_machine(service):
        sys.exit(f"Service is not a machine: {service}")

    NSENTER.execute_invoke(machine, script)


if __name__ == "__main__":
    main()
