import pytest

from nspawn.support.aspect import *


def test_aspect_logger():
    print()

    @aspect_logger()
    def NORMAL(*args, **kwargs) -> None:
        pass

    NORMAL('a', 'b', k1='v1', k2='v2')

    @aspect_logger()
    def EXPLODE(*args, **kwargs) -> None:
        raise RuntimeError("hello-kitty")

    with pytest.raises(Exception) as trap_info:
        EXPLODE('a', 'b', k1='v1', k2='v2')
    print(trap_info)
