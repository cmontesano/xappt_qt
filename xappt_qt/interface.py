import os
import sys

from PySide2 import QtWidgets

import xappt
from xappt import BaseTool

from xappt_qt.dark_palette import apply_palette

from xappt_qt.gui.run_dialog import RunDialog

from xappt_qt.constants import *

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    class __QtInterfaceInner:
        def __init__(self):
            self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
            apply_palette(self.app)

        def exec_(self):
            if self.app.property(APP_PROPERTY_RUNNING):
                return
            self.app.setProperty(APP_PROPERTY_RUNNING, True)
            self.app.exec_()

        def exit(self, return_code=0):
            self.app.exit(return_code)

    instance = None

    def __new__(cls):
        if not QtInterface.instance:
            QtInterface.instance = QtInterface.__QtInterfaceInner()
        return super().__new__(cls)

    def __init__(self):
        super().__init__()
        self.runner = RunDialog()
        self.runner.btnOk.clicked.connect(self.on_run)
        self.runner.btnClose.clicked.connect(self.on_close)

    @classmethod
    def name(cls) -> str:
        return APP_INTERFACE_NAME

    def invoke(self, plugin: BaseTool, **kwargs):
        self.runner.clear()
        self.runner.set_current_tool(plugin)
        self.runner.show()
        self.instance.exec_()

    def message(self, message: str):
        xappt.log.info(message)
        QtWidgets.QMessageBox.information(self.runner, APP_TITLE, message)

    def warning(self, message: str):
        xappt.log.warning(message)
        QtWidgets.QMessageBox.warning(self.runner, APP_TITLE, message)

    def error(self, message: str):
        xappt.log.error(message)
        QtWidgets.QMessageBox.critical(self.runner, APP_TITLE, message)

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(self.runner, APP_TITLE, message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        self.runner.progressBar.setRange(0, 100)
        self.instance.app.processEvents()

    def progress_update(self, message: str, percent_complete: float):
        self.runner.progressBar.setValue(100.0 * percent_complete)
        self.runner.progressBar.setFormat(message)
        self.instance.app.processEvents()

    def progress_end(self):
        self.runner.progressBar.setValue(0)
        self.runner.progressBar.setFormat("")
        self.instance.app.processEvents()

    def on_run(self):
        try:
            self.runner.tool_plugin.validate()
        except xappt.ParameterValidationError as e:
            self.message(str(e))
            return
        self.runner.btnOk.setEnabled(False)
        self.runner.tool_widget.setEnabled(False)
        result = self.runner.tool_plugin.execute(interface=self)
        if result != 0:
            self.runner.btnOk.setEnabled(True)
            self.runner.tool_widget.setEnabled(True)

    def on_close(self):
        self.runner.close()
