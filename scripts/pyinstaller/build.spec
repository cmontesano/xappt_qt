#!/usr/bin/env python
import importlib.resources
import os
import pathlib
import platform

from PyInstaller.building.build_main import Analysis, BUNDLE
from PyInstaller.building.api import EXE, PYZ

import xappt
import xappt_qt.main


block_cipher = None
exe_name = os.environ.get("XAPPT_EXE_NAME", xappt.__name__)
exe_version = os.environ.get("XAPPT_EXE_VERSION", xappt_qt.version_str)

if platform.system() == "Windows":
    exe_console = os.environ.get("XAPPT_EXE_CONSOLE", "0") == "1"
    exe_strip = False
    exe_version_file = os.environ.get("XAPPT_EXE_VERSION_FILE")
    icon_file_name = "appicon.ico"
else:
    if platform.system() == "Darwin":
        icon_file_name = "appicon.icns"
    else:
        icon_file_name = None
    exe_console = True
    exe_strip = True
    exe_version_file = None

if icon_file_name is not None:
    with importlib.resources.path("xappt_qt.resources.icons", icon_file_name) as path:
        exe_icon = str(path)
else:
    exe_icon = None

a = Analysis(
    [pathlib.Path(xappt_qt.main.__file__).absolute()],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['./hooks'],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

data_targets = (
    PYZ(a.pure, cipher=block_cipher),
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
)

exe_kwargs = {
    'exclude_binaries': False,
    'name': exe_name,
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': exe_strip,
    'upx': False,
    'console': exe_console,
}

if exe_icon is not None:
    exe_kwargs['icon'] = exe_icon

if exe_version_file is not None and os.path.isfile(exe_version_file):
    exe_kwargs['version'] = exe_version_file

exe = EXE(*data_targets, **exe_kwargs)


if platform.system() == "Darwin":
    app = BUNDLE(
        exe,
        appname=exe_name,
        version=exe_version,
        name=f"{exe_name}.app",
        icon=exe_icon
    )
