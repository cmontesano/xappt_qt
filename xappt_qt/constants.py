import os
import pathlib
import platform

__all__ = [
    'APP_INTERFACE_NAME',
    'APP_PACKAGE_NAME',
    'APP_TITLE',
    'APP_PROPERTY_RUNNING',
    'APP_CONFIG_PATH',
    'APP_CONFIG_FILE',
]


def user_data_path() -> pathlib.Path:
    if platform.system() == "Windows":
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        key_value, key_type = winreg.QueryValueEx(key, "AppData")
        ans = pathlib.Path(key_value).resolve(strict=False)
    elif platform.system() == 'Darwin':
        ans = pathlib.Path('~/Library/Application Support/').expanduser()
    elif platform.system() == 'Linux':
        ans = pathlib.Path(os.getenv('XDG_DATA_HOME', "~/.local/share")).expanduser()
    else:
        raise NotImplementedError

    return ans


APP_INTERFACE_NAME = "qt"
APP_PACKAGE_NAME = "xappt_qt"
APP_TITLE = "Xappt QT"
APP_PROPERTY_RUNNING = "running"
APP_CONFIG_PATH = user_data_path().joinpath(APP_PACKAGE_NAME)
APP_CONFIG_FILE = os.path.join(APP_CONFIG_PATH, "settings.cfg")
