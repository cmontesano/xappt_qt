#!/usr/bin/env python3
import os
import pathlib
import re
import shlex
import shutil
import subprocess

from typing import Pattern


ROOT_PATH = pathlib.Path(__file__).absolute().parent.parent

CONVERTERS = (
    {
        "source": ROOT_PATH.joinpath("resources", "ui"),
        "destination": ROOT_PATH.joinpath("xappt_qt", "gui", "ui"),
        "extensions": [".ui"],
        "executable": "pyuic5",
        "replacements": (
            ("import icons_rc", "from xappt_qt.gui.resources import icons"),
            (re.compile(r"# Form implementation generated from reading ui file .*"), ""),
        ),
    },
    {
        "source": ROOT_PATH.joinpath("resources", "qrc"),
        "destination": ROOT_PATH.joinpath("xappt_qt", "gui", "resources"),
        "extensions": [".qrc"],
        "executable": "pyrcc5",
    },
)


class ConvertPath:
    def __init__(self, **kwargs):
        binary_path = shutil.which(kwargs['executable'])
        if binary_path is None:
            raise RuntimeError(f"{kwargs['executable']} not found")

        self.binary: str = binary_path
        self.source: pathlib.Path = kwargs['source']
        self.destination: pathlib.Path = kwargs['destination']
        self.extensions: list[str] = kwargs['extensions']
        self.replacements = kwargs.get("replacements")

    def convert(self):
        for root, dirs, files in os.walk(self.source):
            root_path = pathlib.Path(root)
            for f in files:
                file_path = root_path.joinpath(f)
                if file_path.suffix.lower() not in self.extensions:
                    continue
                output_path = self.destination.joinpath(file_path.relative_to(self.source)).with_suffix(".py")

                self.convert_file(file_path, output_path)
                self.process_replacements(output_path)

    def convert_file(self, source_file: pathlib.Path, destination_file: pathlib.Path):
        command = (self.binary, str(source_file), "-o", str(destination_file))
        if os.name == "nt":
            print(subprocess.list2cmdline(command))
        else:
            print(shlex.join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {result.returncode}")

    def replace_line(self, line) -> str:
        for search, replace in self.replacements:
            if isinstance(search, str):
                if line == search:
                    return replace
            if isinstance(search, Pattern):
                match = search.match(line)
                if match is not None:
                    return replace
        return line

    def process_replacements(self, target_file: pathlib.Path):
        if not self.replacements:
            return
        target_temp = target_file.with_suffix(".tmp")
        with target_file.open("r") as fp_in, target_temp.open("w") as fp_out:
            for line in fp_in:
                line = self.replace_line(line.rstrip())
                fp_out.write(line)
                fp_out.write("\n")
        target_file.unlink()
        target_temp.rename(target_file)


def run_converters():
    for converter in CONVERTERS:
        ConvertPath(**converter).convert()


if __name__ == '__main__':
    run_converters()
