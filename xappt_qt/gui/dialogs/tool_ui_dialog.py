import importlib.resources
from itertools import chain
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

import xappt

from xappt_qt.gui.application import get_application
from xappt_qt.gui.ui.tool_interface import Ui_ToolInterface
from xappt_qt.gui.widgets.console import ConsoleWidget
from xappt_qt.gui.widgets.tool_page.widget import ToolPage


class ToolUI(QtWidgets.QDialog, Ui_ToolInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = get_application()

        self.current_tool: Optional[xappt.BaseTool] = None

        self.setupUi(self)
        self.set_window_attributes()

        self.console = ConsoleWidget()
        self.setup_console()

    def set_tool_enabled(self, enabled: bool = True):
        self.toolContainer.setEnabled(enabled)

    def set_window_attributes(self):
        mw = QtWidgets.QMainWindow()
        flags = mw.windowFlags()
        mw.deleteLater()
        self.setWindowFlags(flags)
        self.setWindowIcon(self.app.app_icon)
        with importlib.resources.path("xappt_qt.resources.icons", "help.svg") as path:
            self.btnHelp.setIcon(QtGui.QIcon(str(path)))

    def setup_console(self):
        font_size = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.GeneralFont).pointSizeF()
        mono_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono_font.setPointSizeF(font_size)
        self.console.setFont(mono_font)
        self.consoleContainer.layout().addWidget(self.console)
        self.hide_console()

    def clear_loaded_tool(self):
        layout: QtWidgets.QVBoxLayout = self.toolContainer.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_tool(self, tool_instance: xappt.BaseTool):
        self.clear_loaded_tool()
        self.current_tool = tool_instance
        widget = ToolPage(self.current_tool)

        layout: QtWidgets.QVBoxLayout = self.toolContainer.layout()
        layout.addWidget(self.wrap_widget(widget))

        self.set_tab_order(widget)

    def set_tab_order(self, tool_widget: ToolPage):
        ui_widgets = [self.btnHelp, self.btnRun, self.btnAdvance, self.btnRunAndAdvance]
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
    def wrap_widget(widget: ToolPage) -> QtWidgets.QWidget:
        scroller = QtWidgets.QScrollArea()
        scroller.setWidgetResizable(True)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(widget)

        if not widget.vertical_expand:
            layout.addItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        container.setFocusPolicy(QtCore.Qt.NoFocus)
        container.setLayout(layout)
        scroller.setFocusPolicy(QtCore.Qt.NoFocus)
        scroller.setWidget(container)

        return scroller

    def show_console(self):
        if self.splitter.sizes()[1] > 0:
            return
        half_height = int(self.height() * 0.5)
        self.splitter.setSizes((half_height, half_height))

    def hide_console(self):
        self.splitter.setSizes((self.height(), 0))

    def write_stdout(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.console.write_stdout(line)
        self.app.processEvents()

    def write_stderr(self, text: str):
        self.show_console()
        for line in text.splitlines():
            self.console.write_stderr(line)
        self.app.processEvents()
