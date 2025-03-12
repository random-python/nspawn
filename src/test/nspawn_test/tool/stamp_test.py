import os

from nspawn.tool.stamp import *

# from datetime import datetime

source = "2019-05-06T19:18:22"
instant = datetime.fromisoformat(source)


def test_date_time_iso():
    target = date_time_iso(instant)
    print()
    print(target)
    assert target == "20190506T191822"


def test_date_path():
    target = date_path(instant)
    print()
    print(target)
    assert target == "2019/05/06"


def test_date_dots():
    target = date_dots(instant)
    print()
    print(target)
    assert target == "2019.05.06"


def test_date_dash():
    target = date_dash(instant)
    print()
    print(target)
    assert target == "2019-05-06"


def test_build_stamp():
    stamp_value = build_stamp(instant)
    print()
    print(stamp_value)
    assert stamp_value == "20190506-191822-000000"


def test_build_epoch_default():
    stamp_value = build_epoch()
    build_value = datetime.now().replace(day=1)
    print()
    print(stamp_value)
    assert stamp_value.date() == build_value.date()


def test_build_epoch_environ():
    os.environ[NSPAWN_BUILD_EPOCH] = "2020-12-01"
    stamp_value = build_epoch()
    print()
    print(stamp_value)
    assert stamp_value == datetime(2020, 12, 1, 0, 0, 0)
