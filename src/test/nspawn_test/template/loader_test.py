
from nspawn.template.loader import *

from nspawn.base.machine import MachineMeta, machine_result_from_url
from nspawn.base.machine import MachineStore
from nspawn.base.machine import MachineResult
from nspawn import CONFIG
import platform
from nspawn.tool import stamp

build_stamp = stamp.build_stamp()

epoch = "3.10"
release = f"{epoch}.3"
hardware = platform.machine()
image_url = f"file://localhost/tmp/nspawn/repo/alpine/base/default-{release}-{hardware}.tar.gz"
booter_url = f"http://dl-cdn.alpinelinux.org/alpine/v{epoch}/releases/{hardware}/alpine-minirootfs-{release}-{hardware}.tar.gz"


def test_this_template():
    print()
    file_name = CONFIG['machine']['template']
    machine_template = f"{file_name}"
    template = this_template(machine_template)
    print(template)


def test_file_template():
    print()
    file_name = CONFIG['machine']['template']
    machine_template = f"{this_dir()}/{file_name}"
    template = file_template(machine_template)
    print(template)


def test_machine_service():
    print()

    machine_name = f"tester-{build_stamp}"
    machine_template = CONFIG['machine']['template']
    machine_meta = MachineMeta(machine_name, machine_template)
    machine_result = machine_result_from_url(booter_url, machine_meta)
    machine_result.profile_bucket.with_command(['/bin/init'])
    print(machine_result)

    service_text = machine_service(machine_result)
    print(service_text)
