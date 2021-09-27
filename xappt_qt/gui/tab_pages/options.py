from PyQt5 import QtCore

from xappt_qt.constants import ToolViewType
from xappt_qt.gui.ui.browser_tab_options import Ui_tabOptions
from xappt_qt.gui.tab_pages.base import BaseTabPage


class OptionsTabPage(BaseTabPage, Ui_tabOptions):
    options_changed = QtCore.pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setupUi(self)

        self.populate_tool_view_type_combo()

        self.chkMinimizeToTray.stateChanged.connect(self.options_changed.emit)
        self.chkStartMinimized.stateChanged.connect(self.options_changed.emit)
        self.cmbToolViewType.currentIndexChanged.connect(self.options_changed.emit)

    def populate_tool_view_type_combo(self):
        self.cmbToolViewType.clear()
        for value in ToolViewType:
            name: str = value.name
            if name.startswith("VIEW_"):
                name = name[5:]
            entry = name.replace("_", " ").title()
            self.cmbToolViewType.addItem(entry, value.value)

    def disable_tray_icon(self):
        self.chkMinimizeToTray.setChecked(False)
        self.chkMinimizeToTray.setEnabled(False)

    def settings(self) -> dict:
        return {
            'minimize_to_tray': self.chkMinimizeToTray.isChecked(),
            'start_minimized': self.chkStartMinimized.isChecked(),
            'view_type': self.cmbToolViewType.currentData(),
        }

    def apply_settings(self, settings_dict: dict):
        if self.chkMinimizeToTray.isEnabled():
            self.chkMinimizeToTray.setChecked(settings_dict.get('minimize_to_tray', True))
        else:
            self.chkMinimizeToTray.setChecked(False)
        self.chkStartMinimized.setChecked(settings_dict.get('start_minimized', False))
        view_type = settings_dict.get('view_type', ToolViewType.VIEW_SMALL_ICONS.value)
        index = max(0, self.cmbToolViewType.findData(view_type))
        self.cmbToolViewType.setCurrentIndex(index)
