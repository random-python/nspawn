import socket
from contextlib import closing


def localhost_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as ser:
        ser.bind(('localhost', 0))
        ser.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return ser.getsockname()[1]
