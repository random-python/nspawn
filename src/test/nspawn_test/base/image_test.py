import textwrap

from nspawn.base.image import *

from nspawn import CONFIG

CONFIG['storage']['root'] = "/var/lib/nspawn.test"

import nspawn_test.server
import nspawn_test.network


def test_image_get():
    url = "http://dl-cdn.alpinelinux.org/alpine/v3.9/releases/x86_64/alpine-minirootfs-3.9.4-x86_64.tar.gz"
    print()
    perform_image_get(url)


def test_image_store():
    url = "http://host/arch/base/server.tar.gz"
    image_store = image_store_from_url(url)
    print()
    print(image_store)


def test_image_meta_default():
    print()
    url = "http://host/arch/base/server.tar.gz"
    default = ImageMeta(url)
    print(default)


def test_image_meta_codec():
    print()
    image_url = "http://source/arch/base/server.tar.gz"
    overlay_url_list = ["http://source1/arch/base/server.tar.gz", "http://source2/arch/base/server.tar.gz"]
    profile_command = None
    profile_entry_list = [
        'Bind=/root:/root',
        'Environment=TEST_1=one',
        'Environment=TEST_2=A space B',
        'Environment=TEST_3=A space B space C',
        'Environment=TEST_4=A colon : colon C',
    ]
    source = ImageMeta(image_url, overlay_url_list, profile_command, profile_entry_list)
    src_text = image_meta_encode(source)
    print(src_text)
    target = image_meta_decode(src_text)
    dst_text = image_meta_encode(target)
    print(dst_text)
    assert src_text == dst_text
    assert source == target


def test_image_meta_decode():
    print()
    text = """
    image_url: http://source/arch/base/server.tar.gz
    overlay_url_list: ['http://source1/arch/base/server.tar.gz', 'http://source2/arch/base/server.tar.gz']
    profile_command: null
    profile_entry_list: ['Bind=/root:/root', Environment=TEST_1=one, Environment=TEST_2=A
        space B, Environment=TEST_3=A space B space C, 'Environment=TEST_4=A colon : colon
        C']
    """
    src_text = textwrap.dedent(text)
    image_meta = image_meta_decode(src_text)
    print(image_meta)
    assert image_meta.image_url == "http://source/arch/base/server.tar.gz"
    assert image_meta.overlay_url_list == ['http://source1/arch/base/server.tar.gz', 'http://source2/arch/base/server.tar.gz']
    assert image_meta.profile_command == None
    assert image_meta.profile_entry_list == [
        'Bind=/root:/root',
        'Environment=TEST_1=one',
        'Environment=TEST_2=A space B',
        'Environment=TEST_3=A space B space C',
        'Environment=TEST_4=A colon : colon C',
    ]

# def test_image_build_url():
#     src_url = "http://dl-cdn.alpinelinux.org/alpine/v3.9/releases/x86_64/alpine-minirootfs-3.9.4-x86_64.tar.gz"
#     dst_url = image_build_url(src_url, "tester")
#     print()
#     print(dst_url)


def xxx_test_image_store_get_put():

    print()

    port = nspawn_test.network.localhost_free_port()

    server = nspawn_test.server.HttpServer(port=port)

    server.start()

    src_url = "http://dl-cdn.alpinelinux.org/alpine/v3.9/releases/x86_64/alpine-minirootfs-3.9.4-x86_64.tar.gz"
    src_store = image_store_from_url(src_url)
#     print(f"archive_path={src_store.archive_path()}")
#     print(f"extract_path={src_store.extract_path()}")

    perform_image_erase_path(src_store)
    src_store = perform_image_get_steps(src_store)
    print(src_store)

    dst_url = f"http://localhost:{port}/alpine/alpine-minirootfs-3.9.4-x86_64.tar.gz"
    dst_store = image_store_from_url(dst_url)
#     print(f"archive_path={dst_store.archive_path()}")
#     print(f"extract_path={dst_store.extract_path()}")

    perform_image_move(src_store, dst_store)

    perform_image_put_steps(dst_store)

    server.stop()

    print("###")
