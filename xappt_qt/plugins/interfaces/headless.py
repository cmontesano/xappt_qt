import importlib.resources
import sys

from typing import Optional

from PyQt5 import QtWidgets, QtCore

import xappt

from xappt_qt.constants import *
from xappt_qt.gui.application import get_application


class HeadlessInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = get_application()

        self.progress_dialog = QtWidgets.QProgressDialog()

    def setup_progress_dialog(self):
        self.progress_dialog.setMinimumWidth(600)

        flags = self.progress_dialog.windowFlags()
        flags = flags & ~QtCore.Qt.WindowContextHelpButtonHint  # noqa
        self.progress_dialog.setWindowFlags(flags)

        self.progress_dialog.canceled.connect(self.abort)

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        self.progress_dialog.setWindowTitle(f"{plugin.name()} - {APP_TITLE}")
        return plugin.execute(**kwargs)

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
        self.setup_progress_dialog()
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
        self.progress_dialog.canceled.disconnect(self.abort)
        self.progress_dialog.close()
        self.app.processEvents()

    def run(self, **kwargs) -> int:
        return super().run(**kwargs)

    def abort(self):
        if self.command_runner.running:
            self.command_runner.abort()
        raise SystemExit("Aborted by user")
