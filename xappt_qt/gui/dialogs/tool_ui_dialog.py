from collections import deque, namedtuple
from contextlib import contextmanager
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

import xappt
from xappt_qt import config
from xappt_qt.gui.ui.tool_interface import Ui_ToolInterface
from xappt_qt.gui.widgets.tool_page.widget import ToolPage

OutputLine = namedtuple("OutputLine", ("text", "stream"))


class ToolUI(QtWidgets.QDialog, Ui_ToolInterface):
    STREAM_STDOUT = 0
    STREAM_STDERR = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.output_buffer_raw = deque(maxlen=config.console_line_limit)
        self.output_buffer_html = deque(maxlen=config.console_line_limit)

        self.current_tool: Optional[xappt.BaseTool] = None
        self.saved_size: tuple[int, int] = (-1, -1)
        self.saved_position: tuple[int, int] = (-1, -1)

        self.setupUi(self)
        self.set_window_attributes()
        self.set_console_attributes()

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)
        if self.saved_size > (1, 1):
            self.setGeometry(0, 0, *self.saved_size)
        if self.saved_position >= (0, 0):
            self.move(*self.saved_position)

    @contextmanager
    def tool_executing(self):
        self.stackedWidget.setEnabled(False)
        self.btnNext.setEnabled(False)
        try:
            yield
        finally:
            self.stackedWidget.setEnabled(True)
            self.btnNext.setEnabled(True)

    def set_window_attributes(self):
        flags = QtCore.Qt.Window
        flags |= QtCore.Qt.WindowCloseButtonHint
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        self.setWindowFlags(flags)
        self.setWindowIcon(QtGui.QIcon(":/svg/appicon"))

    def set_console_attributes(self):
        font_size = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.GeneralFont).pointSizeF()
        mono_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono_font.setPointSizeF(font_size)
        self.txtConsole.setFont(mono_font)
        self.hide_console()

    def clear_loaded_tools(self):
        while self.stackedWidget.count():
            widget = self.stackedWidget.widget(0)
            self.stackedWidget.removeWidget(widget)
            widget.deleteLater()

    def load_tool(self, tool_instance: xappt.BaseTool):
        self.clear_loaded_tools()
        self.current_tool = tool_instance
        self.create_tool_widget()

    def create_tool_widget(self):
        tool_page_widget = ToolPage(self.current_tool)

        scroller = QtWidgets.QScrollArea()
        scroller.setWidgetResizable(True)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(tool_page_widget)
        layout.addItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        widget.setLayout(layout)
        scroller.setWidget(widget)

        self.stackedWidget.addWidget(scroller)
        # since we're clearing widgets self.stackedWidget.count() should always be one
        self.stackedWidget.setCurrentIndex(0)

    def show_console(self):
        half_height = int(self.height() * 0.5)
        self.splitter.setSizes((half_height, half_height))

    def hide_console(self):
        self.splitter.setSizes((self.height(), 0))

    def write_to_console(self, text: str, stream: int = STREAM_STDOUT):
        self.show_console()
        for line in text.splitlines():
            self._add_console_line(line, stream=stream)

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

    def _add_console_line(self, s: str, stream: int):
        s = self.convert_leading_whitespace(s)
        color = config.console_color_stdout
        if stream == self.STREAM_STDERR:
            color = config.console_color_stderr

        self.output_buffer_raw.append(OutputLine(text=s, stream=stream))
        self.output_buffer_html.append(f'<span style="color: {color}">{s}</span>')

        self.txtConsole.setHtml("<br />".join(self.output_buffer_html))
        self.txtConsole.moveCursor(QtGui.QTextCursor.End)

        max_scroll = self.txtConsole.verticalScrollBar().maximum()
        self.txtConsole.verticalScrollBar().setValue(max_scroll)
        self.txtConsole.horizontalScrollBar().setValue(0)

        QtWidgets.QApplication.instance().processEvents()
