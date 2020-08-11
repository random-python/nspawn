
from nspawn.wrapper.systemctl import *


def test_version_number():
    print()
    sysctl = SystemCtl()
    version = sysctl.property_VersionNumber()
    print(f"version={version}")


def xxxx_machine_init_pid():
    print()
    sysctl = SystemCtl()
    service = 'systemd-journald.service'
    service_pid = sysctl.machine_init_pid(service)
    print(f"service_pid={service_pid}")


def test_status_present():
    print()
    sysctl = SystemCtl()
    service = 'systemd-journald.service'
    result = sysctl.status(service)
    print(result)
    assert sysctl.has_unit(service)
    assert sysctl.has_active(service)
    assert sysctl.has_enabled(service)


def test_status_missing():
    print()
    sysctl = SystemCtl()
    service = 'systemd-answer-42.service'
    result = sysctl.status(service)
    print(result)
    assert not sysctl.has_unit(service)
    assert not sysctl.has_active(service)
    assert not sysctl.has_enabled(service)


def test_parse_ExecInfo():
    print()
    value = """{ path=/usr/bin/systemd-nspawn ; argv[]=/usr/bin/systemd-nspawn --machine=alpa-base --directory=/var/lib/machines/alpa-base --kill-signal=SIGUSR1 --setenv=TEST_1=solid-value --setenv=TEST_2=value with space --setenv=TEST_3=value : with : colon --setenv=TEST_4=value " with " double quote --quiet --keep-unit --register=yes --network-macvlan=wire0 /sbin/init ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; library=(null) ; status=0/0 }"""
    exec_info = parse_ExecInfo(value)
    print(exec_info)


def test_show_exec_info():
    print()
    sysctl = SystemCtl()
    service = 'systemd-journald.service'
    exec_start = sysctl.show_exec_info('ExecStart', service)
    print(exec_start)
    has_stop = sysctl.has_property('ExecStop', service)
    print(has_stop)
    assert has_stop == False


def test_has_machine():
    print()
    sysctl = SystemCtl()
    service = 'systemd-journald.service'
    has_machine = sysctl.has_machine(service)
    print(has_machine)
    assert has_machine == False
