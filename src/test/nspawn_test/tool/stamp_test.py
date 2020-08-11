from nspawn.tool.stamp import *

from datetime import datetime

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


def test_build_epoch():
    stamp_value = build_stamp(instant)
    print()
    print(stamp_value)
    assert stamp_value == "20190506-191822-000000"
