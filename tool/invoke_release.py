#!/usr/bin/env python

"""
PyPi release
"""

# dependency:
# * https://archlinux.org/packages/extra/any/python-build/
# * https://archlinux.org/packages/extra/any/twine/
# * $HOME/.pypirc

import os

project_dir = "./.."  # base_dir()

os.chdir(project_dir)
os.system("rm -rf dist/")
os.system("python -m build --wheel") # keep order
os.system("twine upload dist/*")

#
#
#
