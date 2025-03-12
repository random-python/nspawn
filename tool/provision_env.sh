#!/usr/bin/env bash

#
#
#

source ./arkon.sh 

sudo rm -rf $pyenv_dir
mkdir    -p $pyenv_dir

python3 -m venv $pyenv_dir

source $pyenv_dir/bin/activate

pip install --upgrade pip wheel setuptools

pip install -r requirements.txt
pip install -r requirements-dev.txt
