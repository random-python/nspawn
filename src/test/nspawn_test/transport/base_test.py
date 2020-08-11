
import pytest
import urllib

from nspawn.transport.base import *


def test_url_file():
    print()
    url = "file://localhost/path/folder?t1=123,t2=234#a=b"
    result = urllib.parse.urlparse(url)
    print(result)
    assert result.hostname == 'localhost'
    assert result.port == None


def test_url_http():
    print()
    url = "http://image:8080/path/folder?t1=123,t2=234#a=b"
    result = urllib.parse.urlparse(url)
    print(result)
    assert result.hostname == 'image'
    assert result.port == 8080


def test_http_head():
    print()
    remote_url = "https://raw.githubusercontent.com/random-python/nspawn/master/readme.md"
    provider = transport_provider(remote_url)
    head_dict = provider.remote_head(remote_url)
    for key, value in head_dict.items():
        print(f"{key}={value}")

def test_http_fail():
    print()
    remote_url = "https://raw.githubusercontent.com/random-python/nspawn/master/readme-invalid.md"
    provider = transport_provider(remote_url)
    with pytest.raises(AssertionError):
        provider.remote_head(remote_url)
