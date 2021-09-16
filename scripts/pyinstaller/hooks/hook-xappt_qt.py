from PyInstaller.utils.hooks import collect_data_files

INCLUDE_EXTENSIONS = (
    "**/*.png",
    "**/*.ico",
    "**/*.svg",
    "**/*.icns",
    "**/*.json",
)

hiddenimports = [
    'xappt_qt.resources.icons',
    'xappt_qt.launcher',
]

datas = collect_data_files("xappt_qt", includes=INCLUDE_EXTENSIONS)
