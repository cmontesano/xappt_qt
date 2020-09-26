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
        self.tool_plugin: Optional[BaseTool] = None
        self.tool_widget: Optional[ToolPage] = None

    def clear(self):
        if self.tool_widget is not None:
            self.gridLayout.removeWidget(self.tool_widget)
            self.tool_widget = None
            self.tool_plugin = None
        self.btnOk.setEnabled(True)

    def set_current_tool(self, tool_plugin: BaseTool):
        if self.tool_widget is not None:
            raise RuntimeError("Clear RunDialog before adding a new tool.")
        self.tool_plugin = tool_plugin
        self.tool_widget = ToolPage(self.tool_plugin)
        self.gridLayout.addWidget(self.tool_widget, 0, 0)
        self.setWindowTitle(tool_plugin.name())
        self.tool_widget.setEnabled(True)


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
            self.runner.btnOk.clicked.connect(self.on_run)
            self.runner.btnClose.clicked.connect(self.on_close)
        self.runner.clear()
        self.runner.set_current_tool(plugin)
        self.runner.show()

    def message(self, message: str):
        QtWidgets.QMessageBox.information(self.runner, "xappt_qt", message)

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(self.runner, "xappt_qt", message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        self.runner.progressBar.setRange(0, 100)

    def progress_update(self, message: str, percent_complete: float):
        self.runner.progressBar.setValue(100.0 * percent_complete)
        self.runner.progressBar.setFormat(message)

    def progress_end(self):
        self.runner.progressBar.setValue(0)
        self.runner.progressBar.setFormat("")

    def on_run(self):
        if self.runner is None:
            return
        try:
            self.runner.tool_plugin.validate()
        except xappt.ParameterValidationError as e:
            self.message(str(e))
            return
        self.runner.btnOk.setEnabled(False)
        self.runner.tool_widget.setEnabled(False)
        self.runner.tool_plugin.execute()

    def on_close(self):
        if self.runner is not None:
            self.runner.hide()
            QtWidgets.QApplication.instance().quit()
