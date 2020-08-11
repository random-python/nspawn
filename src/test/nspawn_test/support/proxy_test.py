
from nspawn.support.proxy import *


def test_proxy_config():
    print()

    entry_map = dict(
        no_proxy="www.google.com",
        http_proxy="http://proxy:3128",
    )

    config = ProxyConfig(entry_map)

    print(config)
    print(config.no_proxy())
    print(config.proxy_for('http'))


def test_proxy_discovery():
    print()

    config = discover_proxy_config()
    config = discover_proxy_config()
    config = discover_proxy_config()

    print(config)
