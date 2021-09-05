import os
import sys

from typing import Optional

from PyQt5 import QtWidgets

import xappt
from xappt_qt.gui.dialogs.tool_ui_dialog import ToolUI

from xappt_qt.gui.utilities.dark_palette import apply_palette

from xappt_qt.constants import *

from xappt_qt.gui.resources import icons  # noqa

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)
        apply_palette(self.app)
        self.ui = ToolUI()

        self.ui.btnNext.clicked.connect(self.on_execute_tool)
        self.on_tool_chain_modified.add(self.update_ui)
        self.on_write_stdout.add(self.ui.write_stdout)
        self.on_write_stderr.add(self.ui.write_stderr)

    @classmethod
    def name(cls) -> str:
        return APP_INTERFACE_NAME

    def on_execute_tool(self):
        tool = self.ui.current_tool
        self.on_tool_completed(self.invoke(tool, **self.tool_data))

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        with self.ui.tool_executing():
            result = plugin.execute(interface=self, **kwargs)
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
        if return_code != 0:
            self.error("tool failed")
            self.ui.reject()
            return

        self._current_tool_index = self.current_tool_index + 1
        try:
            self.load_tool_ui()
        except IndexError:
            self.message("Complete")
            self.ui.accept()

    def load_tool_ui(self):
        tool_class = self.get_tool(self.current_tool_index)
        tool_instance = tool_class(**self.tool_data)
        self.ui.load_tool(tool_instance)
        self.update_ui()

    def run(self) -> int:
        if not len(self._tool_chain):
            return 2
        self._current_tool_index = 0
        tool_class = self.get_tool(self.current_tool_index)
        tool_geo_key = f"{tool_class.collection()}::{tool_class.name()}"

        self.load_window_geo(tool_geo_key)
        self.load_tool_ui()

        result = self.ui.exec()
        self.save_window_geo(tool_geo_key)
        if result == QtWidgets.QDialog.Accepted:
            return 0
        return 1

    def update_ui(self):
        tool_class = self.get_tool(self.current_tool_index)
        self.ui.setWindowTitle(f"{tool_class.name()} - {APP_TITLE}")
        if self.current_tool_index == self.tool_count - 1:
            self.ui.btnNext.setText("Run")
        else:
            self.ui.btnNext.setText("Next")

    def load_window_geo(self, tool_key: str):
        geo = self.data(f"{tool_key}.size")
        if geo is not None:
            self.ui.saved_size = tuple(geo)
        pos = self.data(f"{tool_key}.pos")
        if pos is not None:
            self.ui.saved_position = tuple(pos)

    def save_window_geo(self, tool_key: str):
        self.set_data(f"{tool_key}.size", (self.ui.width(), self.ui.height()))
        self.set_data(f"{tool_key}.pos", (self.ui.geometry().x(), self.ui.geometry().y()))
