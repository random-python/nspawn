
from nspawn.wrapper.nsenter import *


def test_nsenter():
    print()
    machine = "nspawn-image-server"
    script = "id; env; exit"
#     NSENTER.execute_invoke(machine, script)
