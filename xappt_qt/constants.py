import xappt


__all__ = [
    'APP_INTERFACE_NAME',
    'APP_PACKAGE_NAME',
    'APP_TITLE',
    'APP_PROPERTY_RUNNING',
    'APP_CONFIG_PATH',
]


APP_INTERFACE_NAME = "qt"
APP_PACKAGE_NAME = "xappt_qt"
APP_TITLE = "Xappt QT"
APP_PROPERTY_RUNNING = "running"
APP_CONFIG_PATH = xappt.user_data_path().joinpath(APP_PACKAGE_NAME)
