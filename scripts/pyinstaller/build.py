import os
import pathlib
import platform
import shutil
import subprocess
import sys

import xappt
import xappt_qt

ROOT_PATH = pathlib.Path(__file__).absolute().parent
SPEC_PATH = ROOT_PATH.joinpath("build.spec")
DIST_PATH = ROOT_PATH.joinpath("dist")


def clear_directory(path: pathlib.Path):
    if not path.is_dir():
        return
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def main() -> int:
    clear_directory(DIST_PATH)

    os.environ.setdefault("XAPPT_EXE_CONSOLE", "1")
    os.environ.setdefault("XAPPT_EXE_NAME", "xappt")
    os.environ.setdefault("XAPPT_EXE_VERSION", xappt_qt.version_str)
    os.environ.setdefault("XAPPT_COMPANY_NAME", "")
    os.environ.setdefault("XAPPT_COPYRIGHT", "Copyright (c) 2021")

    with xappt.temporary_path() as tmp:
        if platform.system() == "Windows":
            import version_info
            version_file = tmp.joinpath("version_info.txt")
            with open(version_file, "w") as fp:
                fp.write(version_info.version_info_str.strip())
            os.environ.setdefault("XAPPT_EXE_VERSION_FILE", str(version_file))

        command = ('pyinstaller', str(SPEC_PATH), '--onefile')
        proc = subprocess.Popen(command, cwd=str(ROOT_PATH))
        return proc.wait()


if __name__ == '__main__':
    sys.exit(main())
