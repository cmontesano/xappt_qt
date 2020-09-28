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

        self.placeholder.setVisible(False)

        flags = QtCore.Qt.Window
        flags |= QtCore.Qt.WindowCloseButtonHint
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        self.setWindowFlags(flags)
        self.setWindowIcon(QtGui.QIcon(":appicon"))

        self.tool_plugin: Optional[BaseTool] = None
        self.tool_widget: Optional[ToolPage] = None

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
