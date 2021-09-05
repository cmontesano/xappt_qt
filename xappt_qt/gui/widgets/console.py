import os
from collections import deque

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

        self.output_buffer_raw = deque(maxlen=config.console_line_limit)
        self.output_buffer_html = deque(maxlen=config.console_line_limit)

        self.connect_signals()

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
        self.output_buffer_html.clear()
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

        self.output_buffer_raw.append(s)
        self.output_buffer_html.append(f'<span style="color: {color}">{s}</span>')

        self.txtConsole.setHtml("<br />".join(self.output_buffer_html))
        self.txtConsole.moveCursor(QtGui.QTextCursor.End)

        if self.auto_scroll:
            max_scroll = self.txtConsole.verticalScrollBar().maximum()
            self.txtConsole.verticalScrollBar().setValue(max_scroll)
            self.txtConsole.horizontalScrollBar().setValue(0)
