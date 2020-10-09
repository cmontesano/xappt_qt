from typing import Optional

from PySide2 import QtWidgets, QtCore, QtGui

from xappt import BaseTool

from xappt_qt.gui.tool_page import ToolPage
from xappt_qt.gui.ui.runner import Ui_RunDialog

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons


class RunDialog(QtWidgets.QDialog, Ui_RunDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.set_window_attributes()

        self.tool_plugin: Optional[BaseTool] = None
        self.tool_widget: Optional[ToolPage] = None

        self.init_ui()

    def set_window_attributes(self):
        flags = QtCore.Qt.Window
        flags |= QtCore.Qt.WindowCloseButtonHint
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        self.setWindowFlags(flags)
        self.setWindowIcon(QtGui.QIcon(":appicon"))

    def init_ui(self):
        self.placeholder.setVisible(False)

        # noinspection PyArgumentList
        font_size = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.GeneralFont).pointSizeF()
        # noinspection PyArgumentList
        mono_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono_font.setPointSizeF(font_size)
        self.txtOutput.setFont(mono_font)

        self.splitter.setSizes((self.height(), 0))

    def show_console(self):
        half_height = self.height() * 0.5
        self.splitter.setSizes((half_height, half_height))

    def clear(self):
        if self.tool_widget is not None:
            index = self.gridLayout.indexOf(self.tool_widget)
            self.gridLayout.takeAt(index)
            self.tool_widget.deleteLater()
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

    def add_output_line(self, s: str, error: bool = False):
        s = self.convert_leading_whitespace(s)
        self.txtOutput.moveCursor(QtGui.QTextCursor.End)
        if error:
            self.txtOutput.insertHtml(f'<span style="color: #f55">{s}</span><br />\n')
        else:
            self.txtOutput.insertHtml(f'<span style="color: #ccc">{s}</span><br />\n')
        self.txtOutput.moveCursor(QtGui.QTextCursor.End)
        max_scroll = self.txtOutput.verticalScrollBar().maximum()
        self.txtOutput.verticalScrollBar().setValue(max_scroll)
        # noinspection PyArgumentList
        QtWidgets.QApplication.instance().processEvents()

    def add_error_line(self, s: str):
        self.add_output_line(s, True)
