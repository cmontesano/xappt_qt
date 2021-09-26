from PyQt5 import QtCore

from xappt_qt.gui.ui.browser_tab_options import Ui_tabOptions
from xappt_qt.gui.tab_pages.base import BaseTabPage


class OptionsTabPage(BaseTabPage, Ui_tabOptions):
    options_changed = QtCore.pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setupUi(self)
        self.chkMinimizeToTray.stateChanged.connect(self.options_changed.emit)
        self.chkStartMinimized.stateChanged.connect(self.options_changed.emit)

    def disable_tray_icon(self):
        self.chkMinimizeToTray.setChecked(False)
        self.chkMinimizeToTray.setEnabled(False)

    def settings(self) -> dict:
        return {
            'minimize_to_tray': self.chkMinimizeToTray.isChecked(),
            'start_minimized': self.chkStartMinimized.isChecked(),
        }

    def apply_settings(self, settings_dict: dict):
        if self.chkMinimizeToTray.isEnabled():
            self.chkMinimizeToTray.setChecked(settings_dict.get('minimize_to_tray', True))
        else:
            self.chkMinimizeToTray.setChecked(False)
        self.chkStartMinimized.setChecked(settings_dict.get('start_minimized', False))
