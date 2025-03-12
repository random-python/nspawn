
from nspawn.wrapper.machinectl import *


def test_list():
    print()
    mctl = MachineCtl()
    meta_list = mctl.list()
    list(map(print, meta_list))


def test_has_machine():
    print()
    mctl = MachineCtl()
    meta_list = mctl.list()
    if meta_list:
        store = meta_list[0]
        machine = store.MACHINE
        print(mctl.has_machine(machine))
        assert mctl.has_machine(machine)
    assert not mctl.has_machine("<invalid>")
