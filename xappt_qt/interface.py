import os
import sys

from collections import deque
from collections import namedtuple
from typing import Optional, Type

from PyQt5 import QtWidgets, QtGui, QtCore

import xappt  # noqa

from xappt_qt.gui.utilities.dark_palette import apply_palette

from xappt_qt.gui.ui.tool_interface import Ui_ToolInterface

from xappt_qt.constants import *

from xappt_qt import config
from xappt_qt.gui.resources import icons  # noqa
from xappt_qt.gui.widgets.tool_page.widget import ToolPage

os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME

OutputLine = namedtuple("OutputLine", ("text", "stream"))


"""
class QtInterface2(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication.instance()
        self.runner = RunDialog()
        self.__runner_close_event = self.runner.closeEvent
        self.runner.closeEvent = self.close_event
        self.runner.btnOk.clicked.connect(self._on_run)
        self.runner.btnClose.clicked.connect(self.close)
        self.progress_dialog = None
        self.headless = False
        self.on_write_stdout.add(self.write_console_stdout)
        self.on_write_stderr.add(self.write_console_stderr)

    @classmethod
    def name(cls) -> str:
        return APP_INTERFACE_NAME

    def load_window_geo(self):
        assert self.runner.tool_plugin is not None
        tool_key = f"{self.runner.tool_plugin.collection()}::{self.runner.tool_plugin.name()}"
        geo = self.data(f"{tool_key}.geo")
        if geo is not None:
            self.runner.setGeometry(0, 0, *geo)
        pos = self.data(f"{tool_key}.pos")
        if pos is not None:
            self.runner.move(*pos)

    def save_window_geo(self):
        assert self.runner.tool_plugin is not None
        tool_key = f"{self.runner.tool_plugin.collection()}::{self.runner.tool_plugin.name()}"
        self.set_data(f"{tool_key}.geo", (self.runner.width(), self.runner.height()))
        self.set_data(f"{tool_key}.pos", (self.runner.geometry().x(), self.runner.geometry().y()))

    def invoke(self, plugin: BaseTool, **kwargs):
        self.headless = kwargs.get('headless')
        if self.headless:
            center_widget(self.runner)
            result = plugin.execute()
            if self.app.property(APP_PROPERTY_LAUNCHER):
                self.app.quit()
                sys.exit(result)
            return
        self.runner.clear()
        self.runner.set_current_tool(plugin)
        self.runner.show()
        self.load_window_geo()
        for parameter in self.runner.tool_plugin.parameters():
            self.runner.tool_widget.widget_value_updated(param=parameter)
        if kwargs.get('auto_run', False):
            self.runner.tool_plugin.execute()

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
        if self.headless:
            if self.progress_dialog is None:
                self.progress_dialog = QtWidgets.QProgressDialog(self.runner)
            self.progress_dialog.setRange(0, 100)
            self.progress_dialog.setLabelText("")
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.show()
        else:
            self.runner.progressBar.setRange(0, 100)
            self.runner.progressBar.setFormat("")
        self.app.processEvents()

    def progress_update(self, message: str, percent_complete: float):
        progress_value = int(100.0 * percent_complete)
        if self.headless:
            self.progress_dialog.setValue(progress_value)
            self.progress_dialog.setLabelText(message)
        else:
            self.runner.progressBar.setValue(progress_value)
            self.runner.progressBar.setFormat(message)
        self.app.processEvents()

    def progress_end(self):
        if self.headless:
            self.progress_dialog.setValue(0)
            self.progress_dialog.setLabelText("")
            self.progress_dialog.close()
        else:
            self.runner.progressBar.setValue(0)
            self.runner.progressBar.setFormat("")
        self.app.processEvents()

    def write_console_stdout(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.runner.add_output_line(line, error=False)

    def write_console_stderr(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.runner.add_output_line(line, error=True)

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
        if self.command_runner.running:
            self.command_runner.abort()
            self.warning("Process has been terminated.")
            return
        self.runner.close()

    def clear_console(self):
        self.runner.clear_console()

    def show_console(self):
        self.runner.show_console()

    def hide_console(self):
        self.runner.hide_console()

    def is_console_visible(self) -> bool:
        return self.runner.is_console_visible()

    def close_event(self, event: QtGui.QCloseEvent):
        tool_plugin = self.runner.tool_plugin
        if tool_plugin is not None:
            if hasattr(tool_plugin, "can_close"):
                if not tool_plugin.can_close():
                    return event.ignore()
        self.save_window_geo()
        return self.__runner_close_event(event)

"""


class ToolUI(QtWidgets.QDialog, Ui_ToolInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.output_buffer_raw = deque(maxlen=config.console_line_limit)
        self.output_buffer_html = deque(maxlen=config.console_line_limit)

        self.current_tool: Optional[xappt.BaseTool] = None

        self.setupUi(self)
        self.set_window_attributes()

        self.hide_console()

    def set_window_attributes(self):
        flags = QtCore.Qt.Window
        flags |= QtCore.Qt.WindowCloseButtonHint
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        self.setWindowFlags(flags)
        self.setWindowIcon(QtGui.QIcon(":appicon"))

    def load_tool(self, tool_instance: xappt.BaseTool):
        self.current_tool = tool_instance
        self.create_tool_widget()

    def create_tool_widget(self):
        tool_page_widget = ToolPage(self.current_tool)

        scroller = QtWidgets.QScrollArea()
        scroller.setWidgetResizable(True)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(tool_page_widget)
        layout.addItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum,
                                             QtWidgets.QSizePolicy.Expanding))

        widget.setLayout(layout)
        scroller.setWidget(widget)

        self.stackedWidget.addWidget(scroller)

        self.stackedWidget.setCurrentIndex(self.stackedWidget.count() - 1)

    def show_console(self):
        half_height = int(self.height() * 0.5)
        self.splitter.setSizes((half_height, half_height))

    def hide_console(self):
        self.splitter.setSizes((self.height(), 0))

    def write_to_console(self, text: str, error: bool = False):
        self.show_console()
        for line in text.splitlines():
            self.add_output_line(line, error=error)

    @staticmethod
    def convert_leading_whitespace(s: str, tabwidth: int = 4) -> str:
        leading_spaces = 0
        while True:
            if not len(s):
                break
            if s[0] == " ":
                leading_spaces += 1
            elif s[0] == "\t":
                leading_spaces += tabwidth
            else:
                break
            s = s[1:]
        return f"{'&nbsp;' * leading_spaces}{s}"

    def _add_console_line(self, s: str, error: bool = False):
        s = self.convert_leading_whitespace(s)
        color = config.console_color_stdout
        if error:
            color = config.console_color_stderr

        self.output_buffer_raw.append(s)
        self.output_buffer_html.append(f'<span style="color: {color}">{s}</span>')

        self.txtOutput.setHtml("<br />".join(self.output_buffer_html))
        self.txtOutput.moveCursor(QtGui.QTextCursor.End)

        max_scroll = self.txtOutput.verticalScrollBar().maximum()
        self.txtOutput.verticalScrollBar().setValue(max_scroll)
        self.txtOutput.horizontalScrollBar().setValue(0)

        QtWidgets.QApplication.instance().processEvents()


@xappt.register_plugin
class QtInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)
        apply_palette(self.app)
        self.ui = ToolUI()

        self.ui.btnNext.clicked.connect(self.on_execute_tool)
        self.on_tool_added.add(self.update_next_button_caption)
        self.on_write_stdout.add(lambda s: self.ui.write_to_console(s, False))
        self.on_write_stderr.add(lambda s: self.ui.write_to_console(s, True))

    @classmethod
    def name(cls) -> str:
        return APP_INTERFACE_NAME

    def on_execute_tool(self):
        tool = self.ui.current_tool
        self.on_tool_completed(self.invoke(tool, **self.tool_data))

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        return plugin.execute(interface=self, **kwargs)

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
        self.update_next_button_caption()

    def run(self) -> int:
        if not len(self._tool_chain):
            return 2
        self._current_tool_index = 0
        self.load_tool_ui()
        result = self.ui.exec()
        if result == QtWidgets.QDialog.Accepted:
            return 0
        return 1

    def update_next_button_caption(self):  # noqa
        if self.current_tool_index == self.tool_count - 1:
            self.ui.btnNext.setText("Run")
        else:
            self.ui.btnNext.setText("Next")
