from collections import namedtuple
from typing import Callable, Dict, Optional, Union

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QSystemTrayIcon

MenuAction = namedtuple('TrayIconMenuItem', ('on_activate', 'is_visible'))


class TrayIcon(QtCore.QObject):
    def __init__(self, widget: QtWidgets.QWidget, icon: QtGui.QIcon, **kwargs):
        super().__init__()
        self.menu_actions: Dict[str, MenuAction] = {}

        self.on_message_click: Optional[Callable] = kwargs.get('on_message_click')

        self.context_menu = QtWidgets.QMenu()

        self.messages_available = QSystemTrayIcon.supportsMessages()
        self.tray_available = QSystemTrayIcon.isSystemTrayAvailable()

        self.tray_icon = QSystemTrayIcon(widget)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(self.context_menu)

        self._connect_signals()

    def show(self):
        if not self.tray_available:
            return
        self._build_context_menu()
        self.tray_icon.show()

    def destroy(self):
        if not self.tray_available:
            return
        self.tray_icon.deleteLater()

    def add_menu_item(self, name: Optional[str], on_activate: Optional[Callable], is_visible: Optional[Callable]):
        if name is None:
            name = f"--{len(self.menu_actions):02d}"
        self.menu_actions[name] = MenuAction(on_activate, is_visible)

    def _message(self, title: str, message: str,
                 icon: Union[QSystemTrayIcon.MessageIcon, QtGui.QIcon] = QSystemTrayIcon.Information,
                 delay: int = 10000):
        if not self.tray_available:
            return
        if not self.messages_available:
            return
        self.tray_icon.showMessage(title, message, icon, delay)

    def info(self, title: str, message: str, delay: int = 10000):
        self._message(title, message, QSystemTrayIcon.Information, delay)

    def warn(self, title: str, message: str, delay: int = 10000):
        self._message(title, message, QSystemTrayIcon.Warning, delay)

    def critical(self, title: str, message: str, delay: int = 10000):
        self._message(title, message, QSystemTrayIcon.Critical, delay)

    # noinspection PyUnresolvedReferences
    def _connect_signals(self):
        if not self.tray_available:
            return
        self.context_menu.aboutToShow.connect(self._build_context_menu)
        self.context_menu.triggered.connect(self._on_context_menu_action)
        self.tray_icon.messageClicked.connect(self._on_message_clicked)

    def _on_message_clicked(self):
        if self.on_message_click is not None:
            self.on_message_click()

    def _build_context_menu(self):
        self.context_menu.clear()
        for name, menu_item in self.menu_actions.items():
            if name.startswith("--"):
                self.context_menu.addSeparator()
            else:
                if menu_item.is_visible is None or menu_item.is_visible():
                    self.context_menu.addAction(name)

    def _on_context_menu_action(self, action: QtWidgets.QAction):
        if action is None:
            return
        selected_command = action.text()
        on_activate = self.menu_actions[selected_command].on_activate
        if on_activate is not None:
            on_activate()
