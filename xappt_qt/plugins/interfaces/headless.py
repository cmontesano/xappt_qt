import sys

from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

from xappt_qt.constants import *
from xappt_qt.gui.utilities.dark_palette import apply_palette


class HeadlessInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[1:])
        apply_palette(self.app)

        self.progress_dialog = QtWidgets.QProgressDialog()
        self.progress_dialog.setFixedWidth(400)
        self.progress_dialog.setWindowIcon(QtGui.QIcon(":/svg/appicon"))
        self.progress_dialog.setRange(0, 100)
        self.progress_dialog.setLabelText("")
        self.progress_dialog.setCancelButton(None)
        flags = self.progress_dialog.windowFlags()
        flags = flags & ~QtCore.Qt.WindowCloseButtonHint
        flags = flags & ~QtCore.Qt.WindowContextHelpButtonHint
        self.progress_dialog.setWindowFlags(flags)

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        self.progress_dialog.setWindowTitle(f"{plugin.name()} - {APP_TITLE}")
        return plugin.execute(interface=self, **kwargs)

    def message(self, message: str):
        QtWidgets.QMessageBox.information(None, APP_TITLE, message)

    def warning(self, message: str):
        QtWidgets.QMessageBox.warning(None, APP_TITLE, message)

    def error(self, message: str, *, details: Optional[str] = None):
        QtWidgets.QMessageBox.critical(None, APP_TITLE, message)

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(None, APP_TITLE, message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        self.progress_dialog.setValue(0)
        self.progress_dialog.setLabelText("")
        self.progress_dialog.show()
        self.app.processEvents()

    def progress_update(self, message: str, percent_complete: float):
        progress_value = int(100.0 * percent_complete)
        self.progress_dialog.setValue(progress_value)
        self.progress_dialog.setLabelText(message)
        self.app.processEvents()

    def progress_end(self):
        self.progress_dialog.setValue(0)
        self.progress_dialog.setLabelText("")
        self.progress_dialog.close()
        self.app.processEvents()

    def run(self, **kwargs) -> int:
        return super().run(**kwargs)
