from nspawn import CONFIG
from nspawn.support.config import *


def test_config():
    print()
    print(CONFIG)


def test_template():
    print()
    section = 'wrapper/nsenter'
    option = 'option_list'
    config_list = CONFIG.get_list(section, option)
    print(config_list)
    context = dict(
        machine_name="machine",
        command_list=['/bin/ls', '-las'],
    )
    command_list = CONFIG.get_template_list(section, option, context)
    print(command_list)

def test_render_config():
    print()
    print(render_config_parser(CONFIG))
