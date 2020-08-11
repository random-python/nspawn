
from nspawn.tool.network import *


def test_interface_list():
    print()
    face_list = interface_list()
    print(f"face_list={face_list}")


def test_has_internet():
    print()
    has_net = has_internet()
    print(f"has_net={has_net}")


def test_public_address():
    print()
    address = public_address()
    print(f"public_address={address}")


def test_amzon_public_address():
    print()
    address = amazon_public_address()
    print(f"public_address={address}")
