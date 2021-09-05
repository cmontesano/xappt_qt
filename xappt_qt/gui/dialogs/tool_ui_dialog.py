from contextlib import contextmanager
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

import xappt

from xappt_qt.gui.ui.tool_interface import Ui_ToolInterface
from xappt_qt.gui.widgets.console import ConsoleWidget
from xappt_qt.gui.widgets.tool_page.widget import ToolPage


class ToolUI(QtWidgets.QDialog, Ui_ToolInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_tool: Optional[xappt.BaseTool] = None
        self.saved_size: tuple[int, int] = (-1, -1)
        self.saved_position: tuple[int, int] = (-1, -1)

        self.setupUi(self)
        self.set_window_attributes()

        self.console = ConsoleWidget()
        self.setup_console()

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

    def setup_console(self):
        font_size = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.GeneralFont).pointSizeF()
        mono_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono_font.setPointSizeF(font_size)
        self.console.setFont(mono_font)
        self.consoleContainer.layout().addWidget(self.console)
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

    def write_stdout(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.console.write_stdout(line)
        QtWidgets.QApplication.instance().processEvents()

    def write_stderr(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.console.write_stderr(line)
        QtWidgets.QApplication.instance().processEvents()
