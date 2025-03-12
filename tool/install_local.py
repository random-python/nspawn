#!/usr/bin/env python

"""
Use local install for manual testing
"""

from devrepo import base_dir
from devrepo import shell

project_dir = base_dir()

shell("sudo python setup.py install")
shell("sudo rm -rf build")
