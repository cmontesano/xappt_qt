import importlib.resources
from PyQt5 import QtWidgets, QtCore

from xappt_qt.constants import *


class ErrorLabel(QtWidgets.QLabel):
    def __new__(cls):
        instance = super().__new__(cls)
        with importlib.resources.path("xappt_qt.resources.icons", "error.svg") as error_path:
            error_link = f'<a href="#"><img src="{error_path}" /></a>'
        cls.error_link = error_link
        return instance

    def __init__(self):
        super().__init__()

        self._message: str = ""
        self.linkActivated.connect(self._on_link_activated)

        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Ignored)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)

        self.reset()

    def reset(self):
        self._message = ""
        self.setText("")

    def set_error(self, message: str):
        self._message = message
        self.setText(self.error_link)

    def show_error(self):
        if len(self._message):
            QtWidgets.QMessageBox.critical(self.parent(), APP_TITLE, self._message)

    def _on_link_activated(self, _: str):
        self.show_error()
