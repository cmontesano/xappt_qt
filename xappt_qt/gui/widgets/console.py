import os
from typing import Generator

import pyperclip

from PyQt5 import QtGui, QtWidgets

from xappt_qt import config
from xappt_qt.gui.ui.console import Ui_Console


class ConsoleWidget(QtWidgets.QWidget, Ui_Console):
    STREAM_STDOUT = 0
    STREAM_STDERR = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.output_buffer_raw = []

        self.connect_signals()

        self.txtConsole.setTabChangesFocus(True)

        self.word_wrap: bool = config.console_word_wrap
        self.btnWordWrap.setChecked(self.word_wrap)
        self.on_wrap_toggled(self.word_wrap)

        self.auto_scroll: bool = config.console_auto_scroll
        self.btnScrollDown.setChecked(self.auto_scroll)
        self.on_scroll_toggled(self.auto_scroll)

    def connect_signals(self):
        self.btnCopy.clicked.connect(self.on_copy)
        self.btnWordWrap.toggled.connect(self.on_wrap_toggled)
        self.btnScrollDown.toggled.connect(self.on_scroll_toggled)
        self.btnTrash.clicked.connect(self.on_clear)

    def on_copy(self):
        pyperclip.copy(os.linesep.join(self.output_buffer_raw))
        app = QtWidgets.QApplication.instance()
        print(app)
        print(app.property("test"))

    def on_wrap_toggled(self, state: bool):
        self.word_wrap = state
        if self.word_wrap:
            self.txtConsole.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        else:
            self.txtConsole.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

    def on_scroll_toggled(self, state: bool):
        self.auto_scroll = state

    def on_clear(self):
        self.output_buffer_raw.clear()
        self.txtConsole.clear()

    def write_stdout(self, s: str):
        self._write_output(s, self.STREAM_STDOUT)

    def write_stderr(self, s: str):
        self._write_output(s, self.STREAM_STDERR)

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

    def _write_output(self, s: str, stream: int):
        s = self.convert_leading_whitespace(s)
        color = config.console_color_stdout
        if stream == self.STREAM_STDERR:
            color = config.console_color_stderr
        html = f'<span style="color: {color}">{s}</span>'

        self.output_buffer_raw.append(s)
        self.txtConsole.append(html)

        if self.auto_scroll:
            self.txtConsole.moveCursor(QtGui.QTextCursor.End)
            self.txtConsole.moveCursor(QtGui.QTextCursor.StartOfLine)

    def ordered_widgets(self) -> Generator[QtWidgets.QWidget, None, None]:
        yield self.txtConsole
        yield self.btnCopy
        yield self.btnWordWrap
        yield self.btnScrollDown
        yield self.btnTrash
