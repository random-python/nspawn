
from nspawn import CONFIG


def nspawn_tempdir() -> str:
    return CONFIG['storage']['tempdir']
