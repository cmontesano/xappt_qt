import base64
import enum
import os

from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

from xappt_qt.constants import *
from xappt_qt.gui.dialogs.tool_ui_dialog import ToolUI
from xappt_qt.plugins.interfaces.headless import HeadlessInterface
from xappt_qt.gui.application import get_application
from xappt_qt.utilities.tool_attributes import *

os.environ.setdefault('QT_STYLE_OVERRIDE', "Fusion")


class ToolState(enum.Enum):
    LOADED = 0
    RUNNING = 1
    ERROR = 2
    SUCCESS = 3
    UNKNOWN = 99


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = get_application()

        self.ui = ToolUI()

        self.__ui_close_event_orig = self.ui.closeEvent
        self.ui.closeEvent = self.close_event

        self.ui.btnRun.clicked.connect(self.on_run_tool)
        self.ui.btnAdvance.clicked.connect(self.on_next_tool)
        self.ui.btnRunAndAdvance.clicked.connect(self.on_run_and_advance)
        self.ui.btnHelp.clicked.connect(self.on_show_help)
        self.ui.btnAbort.clicked.connect(self.on_abort)

        self.on_write_stdout.add(self.ui.write_stdout)
        self.on_write_stderr.add(self.ui.write_stderr)

        self._tool_geo = {}

        self._tool_state: ToolState = ToolState.UNKNOWN

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

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        return plugin.execute(**kwargs)

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

    def load_tool_ui(self):
        tool_class = self.get_tool(self.current_tool_index)
        tool_instance = tool_class(interface=self, **self.tool_data)
        self.ui.load_tool(tool_instance)
        self.set_tool_state(ToolState.LOADED)

    def run(self, **kwargs) -> int:
        if not len(self._tool_chain):
            return 2

        self._current_tool_index = 0
        tool_class = self.get_tool(self.current_tool_index)

        icon_path = get_tool_icon(tool_class)
        self.ui.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.ui.setWindowTitle(f"{tool_class.name()} - {APP_TITLE}")

        if is_headless(tool_class):
            headless_interface = HeadlessInterface()
            headless_interface.tool_data.update(self.tool_data.copy())
            headless_interface.add_tool(tool_class)
            return headless_interface.run(**kwargs)

        tool_geo_key = f"{tool_class.collection()}::{tool_class.name()}"

        self.load_window_geo(tool_geo_key)
        self.load_tool_ui()

        self.ui.exec()
        self.save_window_geo(tool_geo_key)
        return 0

    def close_event(self, event: QtGui.QCloseEvent):
        if self.command_runner.running or self.current_tool_state() == ToolState.RUNNING:
            if self.ask("A process is currently running.\nDo you want to kill it?"):
                self.command_runner.abort()
                self.warning("The Process has been terminated.")
            event.ignore()
        else:
            self.__ui_close_event_orig(event)

    def on_run_tool(self):
        self.set_tool_state(ToolState.RUNNING)
        tool = self.ui.current_tool
        try:
            tool.validate()
        except xappt.ParameterValidationError as err:
            self.error(str(err))
            self.set_tool_state(ToolState.ERROR)
        else:
            result = self.invoke(tool, **self.tool_data)
            if result == 0:
                self.set_tool_state(ToolState.SUCCESS)
            else:
                self.set_tool_state(ToolState.ERROR)

    def on_next_tool(self):
        self._current_tool_index = self.current_tool_index + 1
        try:
            self.load_tool_ui()
        except IndexError:
            self.ui.close()

    def on_run_and_advance(self):
        self.set_tool_state(ToolState.RUNNING)
        tool = self.ui.current_tool
        try:
            tool.validate()
        except xappt.ParameterValidationError as err:
            self.error(str(err))
            self.set_tool_state(ToolState.ERROR)
        else:
            result = self.invoke(tool, **self.tool_data)
            if result != 0:
                self.set_tool_state(ToolState.ERROR)
                return
            self.on_next_tool()

    def current_tool_state(self) -> ToolState:
        return self._tool_state

    def set_tool_state(self, state: ToolState):
        tool = self.ui.current_tool
        auto_advance = can_auto_advance(tool)

        self.ui.btnRun.setVisible(not auto_advance)
        self.ui.btnAdvance.setVisible(not auto_advance)
        self.ui.btnRunAndAdvance.setVisible(auto_advance)
        self.ui.btnRun.setEnabled(False)
        self.ui.btnAdvance.setEnabled(False)
        self.ui.btnRunAndAdvance.setEnabled(False)

        self.ui.btnHelp.setEnabled(state != ToolState.RUNNING)
        self.ui.btnAbort.setEnabled(state == ToolState.RUNNING)
        self.ui.btnAbort.setVisible(state == ToolState.RUNNING)

        if auto_advance:
            self.set_tool_state_auto_advance(state)
        else:
            self.set_tool_state_no_advance(state)

        self._tool_state = state

    def set_tool_state_auto_advance(self, state: ToolState):
        last_tool = self.current_tool_index == self.tool_count - 1

        if state == ToolState.LOADED:
            self.ui.btnRunAndAdvance.setEnabled(True)
            self.ui.set_tool_enabled(True)
            if last_tool:
                self.ui.btnRunAndAdvance.setText("Run")
            else:
                self.ui.btnRunAndAdvance.setText("Next")
        elif state == ToolState.RUNNING:
            self.ui.set_tool_enabled(False)
            self.ui.btnRunAndAdvance.setEnabled(False)
        elif state == ToolState.ERROR:
            self.ui.set_tool_enabled(True)
            self.ui.btnRunAndAdvance.setEnabled(True)
        elif state == ToolState.SUCCESS:
            pass

    def set_tool_state_no_advance(self, state: ToolState):
        last_tool = self.current_tool_index == self.tool_count - 1

        if state == ToolState.LOADED:
            self.ui.btnRun.setEnabled(True)
            self.ui.set_tool_enabled(True)
            self.ui.set_tool_enabled(True)
        elif state == ToolState.RUNNING:
            self.ui.set_tool_enabled(False)
            self.ui.btnRun.setEnabled(False)
            self.ui.btnAdvance.setEnabled(False)
        elif state == ToolState.ERROR:
            self.ui.set_tool_enabled(True)
            self.ui.btnRun.setEnabled(True)
            self.ui.btnAdvance.setEnabled(False)
        elif state == ToolState.SUCCESS:
            self.ui.btnRun.setEnabled(False)
            self.ui.btnAdvance.setEnabled(True)
            if last_tool:
                self.ui.btnAdvance.setText("Close")

    def on_show_help(self):
        tool = self.ui.current_tool
        if tool is None:
            return
        message = help_text(tool)
        if len(message):
            self.message(message)

    def on_abort(self):
        self.abort()
