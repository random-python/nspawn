import os
from datetime import datetime

#
# environment variable: default build epoch
#
NSPAWN_BUILD_EPOCH = "NSPAWN_BUILD_EPOCH"


def date_time_iso(instant:datetime) -> str:
    return "{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}".format(
        instant.year, instant.month, instant.day,
        instant.hour, instant.minute, instant.second,
    )


def date_path(instant:datetime) -> str:
    return "{:04d}/{:02d}/{:02d}".format(
        instant.year, instant.month, instant.day,
    )


def date_dash(instant:datetime) -> str:
    return "{:04d}-{:02d}-{:02d}".format(
        instant.year, instant.month, instant.day,
    )


def date_dots(instant:datetime) -> str:
    return "{:04d}.{:02d}.{:02d}".format(
        instant.year, instant.month, instant.day,
    )


def build_epoch(instant:datetime=None, day:int=1) -> datetime:
    if instant is None:
        epoch_date = os.environ.get(NSPAWN_BUILD_EPOCH)
        if epoch_date is None:
            instant = datetime.now().replace(day=day)
        else:
            instant = datetime.strptime(epoch_date, "%Y-%m-%d")
    return instant


def build_stamp(instant:datetime=datetime.now()) -> str:
    return instant.strftime("%Y%m%d-%H%M%S-%f")
