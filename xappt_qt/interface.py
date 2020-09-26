import os

from typing import Optional

from PySide2 import QtWidgets

import xappt
from xappt import BaseTool

from .gui.tool_page import ToolPage
from .gui.ui.runner import Ui_RunDialog

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
os.environ[xappt.INTERFACE_ENV] = "qt"


class RunDialog(QtWidgets.QDialog, Ui_RunDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def clear(self):
        w: QtWidgets.QLayoutItem = self.gridLayout.itemAtPosition(0, 0)
        if w is not None and w.widget() is not None:
            self.gridLayout.removeWidget(w.widget())


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.runner: Optional[RunDialog] = None

    @classmethod
    def name(cls) -> str:
        return "qt"

    def invoke(self, plugin: BaseTool, **kwargs):
        if self.runner is None:
            self.runner = RunDialog()
        self.runner.clear()
        self.runner.setWindowTitle(plugin.name())
        w = ToolPage(plugin)
        self.runner.gridLayout.addWidget(w, 0, 0)
        if self.runner.exec_() == self.runner.Accepted:
            try:
                plugin.validate()
            except xappt.ParameterValidationError:
                raise
            plugin.execute()

    def message(self, message: str):
        QtWidgets.QMessageBox.information(None, "xappt_qt", message)

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(None, "xappt_qt", message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        pass

    def progress_update(self, message: str, percent_complete: float):
        self.runner.progressBar.setValue(100.0 * percent_complete)
        self.runner.progressBar.setFormat(message)

    def progress_end(self):
        pass

