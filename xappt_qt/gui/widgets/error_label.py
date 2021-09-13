from PyQt5 import QtWidgets, QtCore

from xappt_qt.constants import *


class ErrorLabel(QtWidgets.QLabel):
    ERROR_LINK = '<a href="#"><img src=":/svg/error" /></a>'

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
        self.setText(self.ERROR_LINK)

    def show_error(self):
        if len(self._message):
            QtWidgets.QMessageBox.critical(self.parent(), APP_TITLE, self._message)

    def _on_link_activated(self, _: str):
        self.show_error()
