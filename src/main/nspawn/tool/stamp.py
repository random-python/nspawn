from datetime import datetime


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


def build_epoch(instant:datetime=datetime.now(), day:int=1) -> datetime:
    return instant.replace(day=day)


def build_stamp(instant:datetime=datetime.now()) -> str:
    return instant.strftime("%Y%m%d-%H%M%S-%f")
