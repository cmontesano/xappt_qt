#!/usr/bin/env python3

import argparse
import os
import platform
import re
import shutil
import sys
import venv

from distutils import sysconfig
from typing import Optional

import xappt

SSH_REGEX = re.compile(r"^(?P<user>[^:]+?)(?::(?P<pass>[^/].*?))?@(?P<host>.*?):(?:(?P<port>\d+)/)?"
                       r"(?P<path>.*?/.*?)$", re.I)
URL_REGEX = re.compile(r"^(?P<protocol>.*?)://(?:(?P<user>.*?)(?::(?P<pass>.*?))?@)?"
                       r"(?P<domain>.*?)(?::(?P<port>\d+))?/(?P<path>.*)$", re.I)

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
    parser.add_argument('-p', '--plugins', action='append', help="Include an external xappt plugins folder or "
                                                                 "git url in the build.")

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
        venv.create(venv_path)

        self.python_bin = os.path.join(venv_path, VENV_BIN, 'python' + PYTHON_EXT)
        self.site_packages = sysconfig.get_python_lib(prefix=venv_path)

        install_command = (sys.executable, '-m', 'pip', 'install', 'pip', '-t', self.site_packages)
        if self.cmd.run(install_command, silent=False).result != 0:
            raise SystemExit("Could not install pip into virtual environment")

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

    def clone_repository(self, url: str, *, destination: str,  branch: Optional[str] = None) -> bool:
        if branch is not None:
            git_command = ("git", "clone", "-b", branch, url, destination)
        else:
            git_command = ("git", "clone", url, destination)
        return self.cmd.run(git_command, silent=False).result == 0

    def install_plugin(self, plugin_path: str, destination: str) -> str:
        plugin_name = os.path.basename(plugin_path)
        plugin_dest = os.path.join(destination, plugin_name)
        if os.path.isdir(plugin_path):
            shutil.copytree(plugin_path, plugin_dest)
            return plugin_dest
        else:
            for regex in (SSH_REGEX, URL_REGEX):
                match = regex.match(plugin_path)
                if match is not None:
                    self.clone_repository(url=plugin_path, destination=plugin_dest)
                    return plugin_dest
        raise NotImplementedError


def get_version(version_path: str) -> str:
    with open(version_path, "r") as fp:
        version_contents = fp.read()

    loc = locals()
    exec(version_contents, {}, loc)
    __version__ = loc['__version__']
    assert __version__ is not None

    return __version__


def update_build(version_path: str, new_build: str):
    version = get_version(version_path)
    with open(version_path, "w") as fp:
        fp.write(f'__version__ = "{version}"\n')
        fp.write(f'__build__ = "{new_build}"\n')


def find_qt():
    import PyQt5

    if platform.system() == "Linux":
        qt5_bin = "lib"
        qt5core_lib = "libQt5Core.so.5"
    elif platform.system() == "Windows":
        qt5_bin = "bin"
        qt5core_lib = "Qt5Core.dll"
    else:
        raise NotImplementedError

    bin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt", qt5_bin)
    if os.path.isfile(os.path.join(bin_path, qt5core_lib)):
        path_var = os.environ['PATH']
        os.environ['PATH'] = bin_path + os.pathsep + path_var


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
        entry_point = os.path.join(tmp, "xappt_qt/main.py")
        assert os.path.isfile(entry_point)

        req_path = os.path.join(repo_path, "requirements.txt")
        if not builder.install_python_requirements(req_path):
            raise SystemExit(f"Error installing requirements {req_path}")

        all_plugin_paths = []
        plugins_destination = os.path.join(tmp, "plugins")
        for plugin in options.plugins:
            plugin_path = builder.install_plugin(plugin, destination=plugins_destination)
            req_file = os.path.join(plugin_path, "requirements.txt")
            if os.path.isfile(req_file):
                builder.install_python_requirements(req_file)
            all_plugin_paths.append(plugin_path)
            sys.path.append(plugin_path)
        if len(all_plugin_paths):
            os.environ[xappt.PLUGIN_PATH_ENV] = os.pathsep.join(all_plugin_paths)

        version_path = os.path.join(repo_path, 'xappt_qt', '__version__.py')
        commit_id = xappt.git_tools.commit_id(repo_path, short=True)
        update_build(version_path, commit_id)

        find_qt()

        nuitka_package = "nuitka==0.6.9.2"
        if not builder.install_python_package(nuitka_package):
            raise SystemExit(f"Error installing {nuitka_package}")

        nuitka_command = ("python", "-m", "nuitka", "--standalone", "--recurse-all",
                          "--plugin-enable=qt-plugins", f"--output-dir={output_path}",
                          entry_point, "--exe")
        builder.cmd.run(nuitka_command, silent=False)

    return 0


if __name__ == '__main__':
    if sys.version_info[:2] < (3, 7):
        raise SystemExit("Python 3.7 or higher is required.")
    sys.exit(main(sys.argv[1:]))
