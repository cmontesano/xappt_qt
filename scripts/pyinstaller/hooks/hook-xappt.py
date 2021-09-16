import os
import pathlib

from distutils import sysconfig
from typing import Generator

from PyInstaller.utils.hooks import collect_submodules


def collect_standard_library() -> Generator[str, None, None]:
    std_lib = pathlib.Path(sysconfig.get_python_lib(standard_lib=True))
    for entry in std_lib.iterdir():
        if entry.name[0] == "_":
            continue
        if entry.name.count("-"):
            continue
        if entry.name.startswith("test"):
            continue
        if entry.is_dir():
            for submodule in collect_submodules(entry.name):
                yield submodule
        else:
            package, ext = os.path.splitext(entry.name)
            if ext.lower() in (".py", ".pyd", ".so"):
                yield entry.stem


hiddenimports = list(collect_standard_library())
