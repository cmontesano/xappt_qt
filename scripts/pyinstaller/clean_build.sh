#!/usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TEMP_PATH="$(mktemp -d)"
trap 'rm -rf -- "$TEMP_PATH"' EXIT

python3 -m venv "$TEMP_PATH"/venv

source "$TEMP_PATH"/venv/bin/activate
python -m pip install wheel
python -m pip install xappt xappt-qt
python -m pip install -r "$SCRIPT_PATH"/requirements.txt

python build.py
