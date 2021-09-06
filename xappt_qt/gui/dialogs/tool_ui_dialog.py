from contextlib import contextmanager
from itertools import chain
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

        self.btnClose.clicked.connect(self.close)

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
        widget = ToolPage(self.current_tool)
        self.stackedWidget.addWidget(self.wrap_widget(widget))
        # since we're clearing widgets self.stackedWidget.count() should always be one
        self.stackedWidget.setCurrentIndex(0)
        self.set_tab_order(widget)

    def set_tab_order(self, tool_widget: ToolPage):
        ui_widgets = [self.btnNext, self.btnClose]
        first_widget: Optional[QtWidgets.QWidget] = None
        last_widget: Optional[QtWidgets.QWidget] = None
        for widget in chain(tool_widget.ordered_widgets(), self.console.ordered_widgets(), ui_widgets):
            if last_widget is None:
                first_widget = widget
            else:
                self.setTabOrder(last_widget, widget)
            last_widget = widget
        if first_widget is not None:
            first_widget.setFocus()

    @staticmethod
    def wrap_widget(widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
        scroller = QtWidgets.QScrollArea()
        scroller.setWidgetResizable(True)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(widget)
        layout.addItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        container.setFocusPolicy(QtCore.Qt.NoFocus)
        container.setLayout(layout)
        scroller.setFocusPolicy(QtCore.Qt.NoFocus)
        scroller.setWidget(container)

        return scroller

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
