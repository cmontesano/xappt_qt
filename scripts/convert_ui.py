#!/usr/bin/env python3
import os
import pathlib
import re
import shlex
import shutil
import subprocess

from typing import Pattern


ROOT_PATH = pathlib.Path(__file__).absolute().parent.parent
SRC_UI_PATH = ROOT_PATH.joinpath("resources", "ui")
DST_UI_PATH = ROOT_PATH.joinpath("xappt_qt", "gui", "ui")

EXE_NAME = "pyuic5"
REPLACEMENTS = (
    # remove file paths to avoid triggering git changes
    (re.compile(r"# Form implementation generated from reading ui file .*"), ""),
)


class ConvertUI:
    def __init__(self):
        binary_path = shutil.which(EXE_NAME)
        if binary_path is None:
            raise RuntimeError(f"'{EXE_NAME}' not found")

        self.binary: str = binary_path

    def convert(self):
        for root, dirs, files in os.walk(SRC_UI_PATH):
            root_path = pathlib.Path(root)
            for f in files:
                file_path = root_path.joinpath(f)
                if file_path.suffix.lower() != ".ui":
                    continue
                output_path = DST_UI_PATH.joinpath(file_path.relative_to(SRC_UI_PATH)).with_suffix(".py")

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

    @staticmethod
    def replace_line(line) -> str:
        for search, replace in REPLACEMENTS:
            if isinstance(search, str):
                if line == search:
                    return replace
            if isinstance(search, Pattern):
                match = search.match(line)
                if match is not None:
                    return replace
        return line

    def process_replacements(self, target_file: pathlib.Path):
        if not REPLACEMENTS:
            return
        target_temp = target_file.with_suffix(".tmp")
        with target_file.open("r") as fp_in, target_temp.open("w") as fp_out:
            for line in fp_in:
                line = self.replace_line(line.rstrip())
                fp_out.write(line)
                fp_out.write("\n")
        target_file.unlink()
        target_temp.rename(target_file)


if __name__ == '__main__':
    ConvertUI().convert()
