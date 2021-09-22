import importlib.resources
import os
import sys

from PyQt5 import QtWidgets, QtGui

from xappt_qt.constants import APP_ICON_ENV


class XapptQtApplication(QtWidgets.QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        custom_icon = os.environ.get(APP_ICON_ENV)
        if custom_icon is not None and os.path.isfile(custom_icon):
            self.app_icon = QtGui.QIcon(str(custom_icon))
        else:
            with importlib.resources.path("xappt_qt.resources.icons", "appicon.svg") as appicon:
                self.app_icon = QtGui.QIcon(str(appicon))

        self.setWindowIcon(self.app_icon)

        from xappt_qt.gui.utilities.style import apply_style
        apply_style(self)


def get_application() -> XapptQtApplication:
    instance = QtWidgets.QApplication.instance()
    return instance or XapptQtApplication(sys.argv[1:])
