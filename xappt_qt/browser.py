import os
import sys


from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

from xappt_qt.gui.ui.browser import Ui_Browser
from xappt_qt.dark_palette import apply_palette
from xappt_qt.constants import *
from xappt_qt.gui.tab_pages import ToolsTabPage, OptionsTabPage, AboutTabPage
import xappt_qt.config

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons


class XapptBrowser(xappt.ConfigMixin, QtWidgets.QMainWindow, Ui_Browser):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(":appicon"))

        self.tools = ToolsTabPage()
        self.options = OptionsTabPage()
        self.about = AboutTabPage()

        self.tabWidget.addTab(self.tools, self.tools.windowTitle())
        self.tabWidget.addTab(self.options, self.options.windowTitle())
        self.tabWidget.addTab(self.about, self.about.windowTitle())
        self.tabWidget.setCurrentIndex(0)

        self.config_path = APP_CONFIG_PATH.joinpath("browser.cfg")
        self.init_config()
        self.load_config()

    def init_config(self):
        self.add_config_item('launch-new-process',
                             saver=lambda: xappt_qt.config.launch_new_process,
                             loader=self.options.chkLaunchNewProcess.setChecked,
                             default=True)
        self.add_config_item('window-size',
                             saver=lambda: (self.width(), self.height()),
                             loader=lambda x: self.setGeometry(0, 0, *x),
                             default=(350, 600))
        self.add_config_item('window-position',
                             saver=lambda: (self.geometry().x(), self.geometry().y()),
                             loader=lambda x: self.set_window_position(*x),
                             default=(-1, -1))

    def set_window_position(self, x: int, y: int):
        if x < 0 or y < 0:
            app = QtWidgets.QApplication.instance()
            cursor_pos = QtGui.QCursor.pos()
            screen = app.screenAt(cursor_pos)

            screen_rect = screen.availableGeometry()
            window_rect = QtCore.QRect(QtCore.QPoint(0, 0), self.frameSize().boundedTo(screen_rect.size()))
            self.resize(window_rect.size())
            self.move(screen_rect.center() - window_rect.center())
        else:
            self.move(x, y)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save_config()
        super().closeEvent(event)
        QtWidgets.QApplication.instance().quit()


def main(args) -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(args)
    apply_palette(app)

    browser = XapptBrowser()
    browser.show()

    app.setProperty(APP_PROPERTY_RUNNING, True)
    return app.exec_()


def entry_point() -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME
    return main(sys.argv)


if __name__ == '__main__':
    sys.exit(entry_point())
