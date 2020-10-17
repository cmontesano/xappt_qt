import os
import sys

from typing import Optional

from PyQt5 import QtWidgets, QtGui

import xappt
from xappt import BaseTool

from xappt_qt.gui.utilities.dark_palette import apply_palette

from xappt_qt.gui.dialogs import RunDialog

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
        self.__runner_close_event = self.runner.closeEvent
        self.runner.closeEvent = self.close_event
        self.runner.btnOk.clicked.connect(self._on_run)
        self.runner.btnClose.clicked.connect(self.close)

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

    def error(self, message: str, *, details: Optional[str] = None):
        xappt.log.error(message, )
        QtWidgets.QMessageBox.critical(self.runner, APP_TITLE, message)
        if details is not None and len(details):
            self.write_console_err(f"\n{details}\n")
            if not self.is_console_visible():
                self.show_console()

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(self.runner, APP_TITLE, message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        self.runner.progressBar.setRange(0, 100)
        self.instance.app.processEvents()

    def progress_update(self, message: str, percent_complete: float):
        self.runner.progressBar.setValue(int(100.0 * percent_complete))
        self.runner.progressBar.setFormat(message)
        self.instance.app.processEvents()

    def progress_end(self):
        self.runner.progressBar.setValue(0)
        self.runner.progressBar.setFormat("")
        self.instance.app.processEvents()

    def _on_run(self):
        try:
            self.runner.tool_plugin.validate()
        except xappt.ParameterValidationError as e:
            self.message(str(e))
            return

        self.enable_ui(False)
        self.runner.tool_plugin.execute(interface=self)
        try:
            self.enable_ui(True)
        except AttributeError:
            # this can happen if the tool asks the interface to close during execute
            pass

    def enable_ui(self, enabled: bool):
        self.runner.btnOk.setEnabled(enabled)
        self.runner.tool_widget.setEnabled(enabled)

    def close(self):
        self.runner.close()

    def clear_console(self):
        self.runner.clear_console()

    def show_console(self):
        self.runner.show_console()

    def hide_console(self):
        self.runner.hide_console()

    def is_console_visible(self) -> bool:
        return self.runner.is_console_visible()

    def write_console_out(self, s: str):
        for line in s.splitlines():
            self.runner.add_output_line(line, error=False)

    def write_console_err(self, s: str):
        for line in s.splitlines():
            self.runner.add_output_line(line, error=True)

    def close_event(self, event: QtGui.QCloseEvent):
        tool_plugin = self.runner.tool_plugin
        if tool_plugin is not None:
            if hasattr(tool_plugin, "can_close"):
                if not tool_plugin.can_close():
                    return event.ignore()
        return self.__runner_close_event(event)
