from PyQt5 import QtWidgets, QtCore, QtGui

from xappt_qt.constants import *


class ErrorLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self._message: str = ""
        self.linkActivated.connect(self._on_link_activated)

        font_size = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.GeneralFont).pointSizeF()
        mono_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono_font.setPointSizeF(font_size * 1.5)
        self.setFont(mono_font)

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
        self.setText('<a href="#" style="color: red; text-decoration:none;">⛔</a>')

    def show_error(self):
        if len(self._message):
            QtWidgets.QMessageBox.critical(self.parent(), APP_TITLE, self._message)

    def _on_link_activated(self, _: str):
        self.show_error()
