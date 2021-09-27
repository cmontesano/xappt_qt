import enum
import os
import xappt

from xappt_qt.utilities import safe_file_name


__all__ = [
    'APP_TITLE_ENV',
    'APP_ICON_ENV',
    'APP_STYLESHEET_ENV',
    'APP_INTERFACE_NAME',
    'APP_PACKAGE_NAME',
    'APP_TITLE',
    'APP_CONFIG_PATH',
    'ToolViewType',
]

# Environment variables
APP_TITLE_ENV = "XAPPT_QT_TITLE"
APP_ICON_ENV = "XAPPT_QT_ICON"
APP_STYLESHEET_ENV = "XAPPT_QT_STYLESHEET"

os.environ.setdefault(APP_TITLE_ENV, "Xappt QT")

APP_INTERFACE_NAME = "qt"
APP_TITLE = os.environ.get(APP_TITLE_ENV)
APP_PACKAGE_NAME = safe_file_name(APP_TITLE)
APP_CONFIG_PATH = xappt.user_data_path().joinpath(APP_PACKAGE_NAME)


class ToolViewType(enum.IntEnum):
    VIEW_SMALL_ICONS = 0
    VIEW_LARGE_ICONS = 1
