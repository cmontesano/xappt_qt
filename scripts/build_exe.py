#!/usr/bin/env python3

import argparse
import os
import platform
import shutil
import sys

from distutils import sysconfig

import xappt

if platform.system() == "Windows":
    VENV_BIN = "Scripts"
    PYTHON_EXT = ".exe"
else:
    VENV_BIN = "bin"
    PYTHON_EXT = ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument('source', help='A git URL to clone for the build.')
    parser.add_argument('-b', '--branch', default="master", help='The branch to check out')
    parser.add_argument('-o', '--output', help='A folder that will contain the built program.')

    return parser


def check_build_requirements():
    if shutil.which("git") is None:
        raise SystemExit("git was not found")
    try:
        import venv
    except ImportError:
        raise SystemExit("venv python module not found")


class Builder:
    def __init__(self, *, work_path: str):
        self.work_path = work_path
        self.cmd = xappt.CommandRunner(cwd=work_path)
        self.python_bin = None
        self.site_packages = None

    def create_venv(self) -> bool:
        venv_path = os.path.join(self.work_path, "venv")
        venv_command = (sys.executable, "-m", "venv", venv_path)
        result = self.cmd.run(venv_command, silent=False)
        if result.result != 0:
            return False

        self.python_bin = os.path.join(venv_path, VENV_BIN, 'python' + PYTHON_EXT)
        self.site_packages = sysconfig.get_python_lib(prefix=venv_path)

        self.cmd.env_path_prepend('PATH', os.path.dirname(self.python_bin))
        self.cmd.env_path_prepend('PATH', os.path.join(self.site_packages, 'bin'))
        self.cmd.env_path_prepend('PYTHONPATH', self.site_packages)
        self.cmd.env_var_add('VIRTUAL_ENV', venv_path)
        self.cmd.env_var_remove('PYTHONHOME')

        return True

    def install_python_package(self, package_name: str) -> bool:
        install_command = (self.python_bin, '-m', 'pip', 'install', package_name, '-t', self.site_packages)
        return self.cmd.run(install_command, silent=False).result == 0

    def install_python_requirements(self, req_file_path: str) -> bool:
        install_command = (self.python_bin, '-m', 'pip', 'install', '-r', req_file_path, '-t', self.site_packages)
        return self.cmd.run(install_command, silent=False).result == 0

    def clone_repository(self, url: str, *, branch: str, destination: str) -> bool:
        git_command = ("git", "clone", "-b", branch, url, destination)
        return self.cmd.run(git_command, silent=False).result == 0


def main(args) -> int:
    check_build_requirements()

    parser = build_parser()
    options = parser.parse_args(args=args)

    output_path = os.path.abspath(options.output)
    if os.path.isdir(output_path):
        raise SystemExit(f"Error, output path exists: {output_path}")

    with xappt.temp_path() as tmp:
        builder = Builder(work_path=tmp)
        if not builder.create_venv():
            raise SystemExit("Virtual environment creation failed")

        repo_path = os.path.join(tmp, "xappt_qt")
        if not builder.clone_repository(options.source, branch=options.branch, destination=repo_path):
            raise SystemExit(f"Error cloning {options.source}")

        req_path = os.path.join(repo_path, "requirements.txt")
        if not builder.install_python_requirements(req_path):
            raise SystemExit(f"Error installing requirements {req_path}")

        nuitka_package = "nuitka==0.6.9.2"
        if not builder.install_python_package(nuitka_package):
            raise SystemExit(f"Error installing {nuitka_package}")

        nuitka_command = ("python", "-m", "nuitka", "--standalone", "--recurse-all", "--plugin-enable=qt-plugins",
                          os.path.join(tmp, "xappt_qt/main.py"), "--exe")
        builder.cmd.run(nuitka_command, silent=False)
        shutil.copytree(os.path.join(tmp, 'browser.dist'), output_path)

    return 0


if __name__ == '__main__':
    if sys.version_info[:2] < (3, 7):
        raise SystemExit("Python 3.7 or higher is required.")
    sys.exit(main(sys.argv[1:]))
