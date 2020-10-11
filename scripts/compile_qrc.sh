#!/usr/bin/env bash

OLD_CWD=$pwd

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QRC_PATH="$(realpath -s "$SCRIPT_PATH/../resources/qrc")"
PY_PATH="$(realpath -s "$SCRIPT_PATH/../xappt_qt/gui/resources")"

cd $QRC_PATH

for i in *.qrc;
  do
    pyrcc5 "$i" -o "$PY_PATH/${i%.*}.py";
  done

cd $OLD_CWD
