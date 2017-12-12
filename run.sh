#!/usr/bin/env bash

if [[ $# -lt 1 ]]; then
    echo usage: $0 TOOL [...]
    exit 1
fi

tool=$1
shift

if [[ ! -e $tool ]]; then
    echo tool $tool not available
    exit 1
fi

BASE_DIRECTORY=${BASE_DIRECTORY:-/opt/tools}

command -v pip >/dev/null 2>&1 || { echo >&2 "pip not installed"; exit 1; }
command -v virtualenv >/dev/null 2>&1 || { echo >&2 "virtualenv not installed"; exit 1; }

pushd $BASE_DIRECTORY

if [[ ! -e .venv-$tool ]]; then
    virtualenv .venv-$tool
    source .venv-$tool/bin/activate
    pip install -r $tool/requirements.txt
else
    source .venv-$tool/bin/activate
fi

pushd $tool
python $tool.py $*
popd

popd
