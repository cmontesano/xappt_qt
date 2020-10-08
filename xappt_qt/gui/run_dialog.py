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

        self.setup_ui()

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
