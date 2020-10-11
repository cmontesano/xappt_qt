#!/usr/bin/env bash

OLD_CWD=$pwd

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_PATH="$(realpath -s "$SCRIPT_PATH/../resources/ui")"
PY_PATH="$(realpath -s "$SCRIPT_PATH/../xappt_qt/gui/ui")"

cd $UI_PATH

for i in *.ui;
  do
    pyuic5 "$i" -o "$PY_PATH/${i%.*}.py";
  done

cd $OLD_CWD
