from PyQt5 import QtWidgets, QtCore

from xappt_qt.gui.ui.browser_tab_options import Ui_tabOptions
import xappt_qt.config


class OptionsTabPage(QtWidgets.QWidget, Ui_tabOptions):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.chkLaunchNewProcess.stateChanged.connect(self.on_launch_new_process_changed)
        self.chkMinimizeToTray.stateChanged.connect(self.on_minimize_to_tray_changed)

    @staticmethod
    def on_launch_new_process_changed(new_state: int):
        xappt_qt.config.launch_new_process = new_state == QtCore.Qt.Checked

    @staticmethod
    def on_minimize_to_tray_changed(new_state: int):
        xappt_qt.config.minimize_to_tray = new_state == QtCore.Qt.Checked
