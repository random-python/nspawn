#!/usr/bin/env python3

import store_id_prog

entry_list = [
    (
        "http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip 192.168.1.103/192.168.1.103 - GET myip=192.168.1.137 myport=3128",
        "http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip",
    ),
    (
        "http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip?AuthParam=1468794966_3ec82d3de3b479a3fc7faec9ca20180b 192.168.1.103/work3 - GET myip=192.168.1.137 myport=3128",
        "http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip",
    ),
    (
        "https://ia803006.us.archive.org/0/items/archlinux_pkg_python-pytoml/python-pytoml-0.1.21-3-any.pkg.tar.xz 192.168.1.103/192.168.1.103 - GET myip=192.168.1.137 myport=3128",
        "https://archive.org.internal/0/items/archlinux_pkg_python-pytoml/python-pytoml-0.1.21-3-any.pkg.tar.xz",
    ),
    (
        "https://archive.archlinux.org/repos/2020/01/01/community/os/x86_64/python-wheel-0.33.6-3-any.pkg.tar.xz 192.168.1.103/work3 - GET myip=192.168.1.137 myport=3128",
        "https://archive.archlinux.org/repos/2020/01/01/community/os/x86_64/python-wheel-0.33.6-3-any.pkg.tar.xz",
    ),
]

for entry in entry_list:
    source = entry[0]
    target = entry[1]
    print(f"---")
    print(f"source: {source}")
    print(f"target: {target}")
    assert target == store_id_prog.produce_id(source)
