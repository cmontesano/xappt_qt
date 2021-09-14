import base64
import os
import sys

from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

from xappt_qt.constants import *
from xappt_qt.gui.dialogs.tool_ui_dialog import ToolUI
from xappt_qt.plugins.interfaces.headless import HeadlessInterface
from xappt_qt.gui.utilities.style import apply_style
from xappt_qt.utilities.tool_attributes import *

os.environ.setdefault('QT_STYLE_OVERRIDE', "Fusion")


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[1:])
        apply_style(self.app)
        self.ui = ToolUI()

        self.__ui_close_event_orig = self.ui.closeEvent
        self.ui.closeEvent = self.close_event

        self.ui.btnNext.clicked.connect(self.on_execute_tool)
        self.on_tool_chain_modified.add(self.update_ui)
        self.on_write_stdout.add(self.ui.write_stdout)
        self.on_write_stderr.add(self.ui.write_stderr)

        self._tool_geo = {}

    def init_config(self):
        self.add_config_item(key="tool_geo",
                             saver=lambda: self._tool_geo,
                             loader=lambda geo: self._tool_geo.update(geo),
                             default=dict())

    def load_window_geo(self, tool_key: str):
        self.load_config()
        geo = self._tool_geo.get(tool_key)
        try:
            self.ui.restoreGeometry(QtCore.QByteArray(base64.b64decode(geo)))
        except TypeError:
            pass

    def save_window_geo(self, tool_key: str):
        geo = bytes(self.ui.saveGeometry())
        self._tool_geo[tool_key] = base64.b64encode(geo).decode('utf8')
        self.save_config()

    @classmethod
    def name(cls) -> str:
        return APP_INTERFACE_NAME

    def on_execute_tool(self):
        tool = self.ui.current_tool

        try:
            tool.validate()
        except xappt.ParameterValidationError as err:
            self.error(str(err))
            return

        self.on_tool_completed(self.invoke(tool, **self.tool_data))

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        with self.ui.tool_executing():
            result = plugin.execute(**kwargs)
        return result

    def message(self, message: str):
        QtWidgets.QMessageBox.information(self.ui, APP_TITLE, message)

    def warning(self, message: str):
        QtWidgets.QMessageBox.warning(self.ui, APP_TITLE, message)

    def error(self, message: str, *, details: Optional[str] = None):
        QtWidgets.QMessageBox.critical(self.ui, APP_TITLE, message)

    def ask(self, message: str) -> bool:
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(self.ui, APP_TITLE, message, buttons=buttons,
                                                    defaultButton=QtWidgets.QMessageBox.No)
        return ask_result == QtWidgets.QMessageBox.Yes

    def progress_start(self):
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setFormat("")
        self.app.processEvents()

    def progress_update(self, message: str, percent_complete: float):
        progress_value = int(100.0 * percent_complete)
        self.ui.progressBar.setValue(progress_value)
        self.ui.progressBar.setFormat(message)
        self.app.processEvents()

    def progress_end(self):
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setFormat("")
        self.app.processEvents()

    def on_tool_completed(self, return_code: int):
        if return_code == 0:
            self._current_tool_index = self.current_tool_index + 1
            try:
                self.load_tool_ui()
            except IndexError:
                pass
            else:
                # don't close if we have another tool
                return
        self.ui.close()

    def load_tool_ui(self):
        tool_class = self.get_tool(self.current_tool_index)
        tool_instance = tool_class(interface=self, **self.tool_data)
        self.ui.load_tool(tool_instance)
        self.update_ui()

    def run(self, **kwargs) -> int:
        if not len(self._tool_chain):
            return 2

        self._current_tool_index = 0
        tool_class = self.get_tool(self.current_tool_index)

        icon_path = get_tool_icon(tool_class)
        self.ui.setWindowIcon(QtGui.QIcon(str(icon_path)))

        if is_headless(tool_class):
            headless_interface = HeadlessInterface()
            headless_interface.add_tool(tool_class)
            return headless_interface.run(**kwargs)

        tool_geo_key = f"{tool_class.collection()}::{tool_class.name()}"

        self.load_window_geo(tool_geo_key)
        self.load_tool_ui()

        self.ui.exec()
        self.save_window_geo(tool_geo_key)
        return 0

    def update_ui(self):
        tool_class = self.get_tool(self.current_tool_index)
        self.ui.setWindowTitle(f"{tool_class.name()} - {APP_TITLE}")
        if self.current_tool_index == self.tool_count - 1:
            self.ui.btnNext.setText("Run")
        else:
            self.ui.btnNext.setText("Next")

    def close_event(self, event: QtGui.QCloseEvent):
        if self.command_runner.running:
            if self.ask("A process is currently running.\nDo you want to kill it?"):
                self.command_runner.abort()
                self.warning("The Process has been terminated.")
            event.ignore()
        else:
            self.__ui_close_event_orig(event)
