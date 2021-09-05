#!/usr/bin/env python3
import os
import pathlib
import shlex
import shutil
import subprocess

ROOT_PATH = pathlib.Path(__file__).absolute().parent.parent
UI_PATH = ROOT_PATH.joinpath("resources", "ui")
PY_PATH = ROOT_PATH.joinpath("xappt_qt", "gui", "ui")

IMPORT_REPLACEMENTS = {
    "import icons_rc": "from xappt_qt.gui.resources import icons",
}


def fix_imports(ui_path: pathlib.Path):
    ui_path_temp = ui_path.with_suffix(".tmp")
    with ui_path.open("r") as fp_in, ui_path_temp.open("w") as fp_out:
        for line in fp_in:
            line = line.rstrip()
            if line in IMPORT_REPLACEMENTS.keys():
                fp_out.write(IMPORT_REPLACEMENTS[line])
            else:
                fp_out.write(line)
            fp_out.write("\n")
    ui_path.unlink()
    ui_path_temp.rename(ui_path)


def scan_ui_files():
    pyuic5_bin = shutil.which("pyuic5")
    if pyuic5_bin is None:
        raise RuntimeError("pyuic5 not found")

    for item in UI_PATH.iterdir():
        if not item.is_file():
            continue
        if item.suffix.lower() != ".ui":
            continue
        ui_path = PY_PATH.joinpath(item.name).with_suffix(".py")
        command = (pyuic5_bin, str(item), "-o", str(ui_path))
        if os.name == "nt":
            print(subprocess.list2cmdline(command))
        else:
            print(shlex.join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {result.returncode}")
        fix_imports(ui_path)


if __name__ == '__main__':
    scan_ui_files()
