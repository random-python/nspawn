#!/usr/bin/env bash

set -e -u

readonly base_dir=$( cd $( dirname "$0" )/.. && pwd )

readonly pyenv_dir=$base_dir/.pyenv

cd $base_dir
[ -d $pyenv_dir ] && source $pyenv_dir/bin/activate

echo "### base_dir=$base_dir"
echo "### pyenv_dir=$pyenv_dir"
