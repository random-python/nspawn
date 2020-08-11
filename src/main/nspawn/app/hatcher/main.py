"""
Hatcher application entry
"""

import os
import runpy
import subprocess

from typing import List, Dict
from urllib.parse import urlparse
from nspawn.app.hatcher.parser import hatcher_parser
from nspawn.wrapper.sudo import SUDO

this_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = f"{this_dir}/service"


def shell(command:List[str]) -> None:
    subprocess.check_call(command)


def service_folder(service:str) -> str:
    folder = f"{service_dir}/{service}"
    return folder


def service_context(service:str) -> Dict[str, str]:
    folder = service_folder(service)
    run_path = f"{folder}/arkon.py"
    context = runpy.run_path(run_path)
    return context


def service_image(service:str) -> str:
    context = service_context(service)
    image_url = context['image_url']
    image_path = urlparse(image_url).path
    return image_path


def has_image(service:str) -> bool:
    image_path = service_image(service)
    return os.path.isfile(image_path)


def perform_list() -> None:
    entry_list = os.listdir(service_dir)
    entry_list.sort()
    for entry in entry_list:
        print(entry)


def perform_build(service:str, option_list:List[str]) -> None:
    folder = service_folder(service)
    command = [f"{folder}/build.py"] + option_list
    shell(command)


def perform_setup(service:str, action:str, option_list:List[str]) -> None:
    folder = service_folder(service)
    command = [f"{folder}/setup.py", f"--action={action}"] + option_list
    shell(command)


def perform_erase(service:str) -> None:
    image_path = service_image(service)
    SUDO.files_delete(image_path)


def main():

    parser = hatcher_parser()

    space = parser.parse_args()
    if space.config :
        option_list = ['--config'] + space.config
    else:
        option_list = []

    if space.command == 'list':
        perform_list()
    else:
        service = space.service
        if not os.path.isdir(service_folder(service)):
            raise RuntimeError(f"Invalid service: {service}")
        if space.command == 'ensure':
            if not has_image(service):
                perform_build(service, option_list)
            perform_setup(service, 'ensure', option_list)
        elif space.command == 'desure':
            perform_setup(service, 'desure', option_list)
            if has_image(service):
                perform_erase(service)
        elif space.command == 'update':
            perform_setup(service, 'desure', option_list)
            perform_build(service, option_list)
            perform_setup(service, 'ensure', option_list)
        else:
            raise RuntimeError(f"Invalid command: {space.command}")


if __name__ == "__main__":
    main()
