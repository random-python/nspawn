
import os

from nspawn.transport.http import *

this_dir = os.path.dirname(__file__)

def test_with_auth_url():
    print()
    curl = Curl()
    remote_url = "http://image/path/package.tar.gz"
    with_auth_url(curl, remote_url)
    print(curl)
    assert 'http://nspawn-image-server/path/package.tar.gz' in curl.full_command()
    assert 'default:default' in curl.full_command()


def test_parse_header_file_1():
    print()
    header_path = f"{this_dir}/curl-head-1.txt"
    header_dict = parse_header_file(header_path)
    print(header_dict)
    assert header_dict['etag'] == '"5d5bcbd4-295ebd"'
    assert header_dict['content-length'] == '2711229'
    assert header_dict['last-modified'] == 'Tue, 20 Aug 2019 10:30:44 GMT'


def test_parse_header_file_2():
    print()
    header_path = f"{this_dir}/curl-head-2.txt"
    header_dict = parse_header_file(header_path)
    print(header_dict)
    assert header_dict['etag'] == '"5d6b53d2-92e939e"'
    assert header_dict['content-length'] == '154047390'
    assert header_dict['last-modified'] == 'Sun, 01 Sep 2019 05:14:58 GMT'
