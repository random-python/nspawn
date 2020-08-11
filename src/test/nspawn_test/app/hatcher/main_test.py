
from nspawn.app.hatcher.main import *


def test_service_image():
    print()
    image_path = service_image('image-server')
    print(image_path)


def test_perform_list():
    print()
    perform_list()
