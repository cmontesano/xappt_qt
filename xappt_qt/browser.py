import base64
import os
import platform
import sys


from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

from xappt_qt.gui.application import get_application
from xappt_qt.gui.ui.browser import Ui_Browser
from xappt_qt.gui.utilities.tray_icon import TrayIcon
from xappt_qt.constants import *
from xappt_qt.gui.tab_pages import ToolsTabPage, OptionsTabPage, AboutTabPage

from xappt_qt.utilities import singleton

DISABLE_TRAY_ICON = platform.system() == "Darwin"


class XapptBrowser(xappt.ConfigMixin, QtWidgets.QMainWindow, Ui_Browser):
    def __init__(self):
        super().__init__()

        self.app = get_application()

        self.setupUi(self)
        self.setWindowTitle(APP_TITLE)

        self.setWindowIcon(self.app.app_icon)
        self.tray_icon = TrayIcon(self, self.app.app_icon)

        self.tools = ToolsTabPage(on_info=self.tray_icon.info, on_warn=self.tray_icon.warn,
                                  on_error=self.tray_icon.critical)
        self.options = OptionsTabPage()
        self.about = AboutTabPage()

        self.tabWidget.addTab(self.tools, self.tools.windowTitle())
        self.tabWidget.addTab(self.options, self.options.windowTitle())
        self.tabWidget.addTab(self.about, self.about.windowTitle())
        self.tabWidget.setCurrentIndex(0)

        self.options.options_changed.connect(self.on_options_changed)
        if DISABLE_TRAY_ICON:
            self.options.disable_tray_icon()

        self.config_path = APP_CONFIG_PATH.joinpath("browser.cfg")
        self.init_config()
        self.load_config()

        self.init_tray_icon()

    def init_config(self):
        self.add_config_item('window-geo',
                             saver=self.save_window_geo,
                             loader=self.load_window_geo,
                             default=None)
        self.add_config_item('settings',
                             saver=lambda: self.options.settings(),
                             loader=lambda x: self.options.apply_settings(x),
                             default={})

    def load_window_geo(self, geo: str):
        try:
            self.restoreGeometry(QtCore.QByteArray(base64.b64decode(geo)))
        except TypeError:
            pass

    def save_window_geo(self) -> str:
        geo = bytes(self.saveGeometry())
        return base64.b64encode(geo).decode('utf8')

    def init_tray_icon(self):
        if DISABLE_TRAY_ICON:
            return

        for category, plugin_list in self.tools.loaded_plugins.items():
            for plugin in plugin_list:
                self.tray_icon.add_menu_item(plugin.name(), on_activate=self.run_tool, data=plugin, group=category)

        self.tray_icon.add_menu_item(None)
        self.tray_icon.add_menu_item("Show", on_activate=self.show, is_visible=self.isHidden)
        self.tray_icon.add_menu_item("Hide", on_activate=self.hide, is_visible=self.isVisible)
        self.tray_icon.add_menu_item(None)
        self.tray_icon.add_menu_item("Quit", on_activate=self.on_quit)
        self.tray_icon.on_trigger = self.on_activate
        self.tray_icon.show()

    def changeEvent(self, event: QtCore.QEvent):
        if not DISABLE_TRAY_ICON:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.windowState() == QtCore.Qt.WindowMinimized:
                    if self.options.settings().get('minimize_to_tray') and self.tray_icon.tray_available:
                        self.hide()
        super().changeEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent):
        if self.options.settings().get('minimize_to_tray') and self.tray_icon.tray_available:
            event.ignore()
            self.hide()
        else:
            self.on_quit()

    def on_activate(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def on_quit(self):
        self.tray_icon.destroy()
        self.save_config()
        self.app.quit()

    def run_tool(self, **kwargs):
        plugin = kwargs.get('data')
        if plugin is None:
            return
        assert issubclass(plugin, xappt.BaseTool)
        self.tools.launch_tool(plugin)

    def on_options_changed(self):
        settings = self.options.settings()
        self.tools.settings_changed(settings)
        self.options.settings_changed(settings)
        self.about.settings_changed(settings)


def main(args) -> int:
    try:
        _ = singleton.SingleInstance(flavor_id='browser')
    except singleton.SingleInstanceException:
        return 1

    app = get_application()

    browser = XapptBrowser()
    if browser.options.settings().get('start_minimized'):
        if not browser.options.settings().get('minimize_to_tray'):
            browser.setWindowState(QtCore.Qt.WindowMinimized)
            browser.show()
    else:
        browser.show()

    return app.exec_()


def entry_point() -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME
    return main(sys.argv)


if __name__ == '__main__':
    sys.exit(entry_point())
