import os
import platform
import subprocess
import sys

from collections import defaultdict
from typing import DefaultDict, List, Optional, Tuple, Type

from PyQt5 import QtWidgets, QtGui, QtCore

import xappt

from xappt_qt.gui.ui.browser import Ui_Browser
from xappt_qt.gui.delegates import SimpleItemDelegate
from xappt_qt.dark_palette import apply_palette
from xappt_qt.constants import *
from xappt_qt.config import default_config, read_config, write_config

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons


class XapptBrowser(QtWidgets.QMainWindow, Ui_Browser):
    ROLE_TOOL_CLASS = QtCore.Qt.UserRole + 1
    ROLE_ITEM_TYPE = QtCore.Qt.UserRole + 2

    ITEM_TYPE_COLLECTION = 0
    ITEM_TYPE_TOOL = 1

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(":appicon"))
        self.treeTools.setItemDelegate(SimpleItemDelegate())

        self.populate_plugins()
        self.connect_signals()

        self.txtSearch.setFocus()

        self.load_settings()

    def load_settings(self):
        config = read_config()
        self.chkLaunchNewProcess.setChecked(config.getboolean('browser', 'launch-new-process'))

    def save_settings(self):
        config = default_config()
        config['browser']['launch-new-process'] = str(self.chkLaunchNewProcess.isChecked())
        write_config(config)

    def connect_signals(self):
        self.treeTools.itemActivated.connect(self.item_activated)
        self.treeTools.itemSelectionChanged.connect(self.selection_changed)

        self.txtSearch.textChanged.connect(self.on_filter_tools)
        # noinspection PyAttributeOutsideInit
        self.__txtSearch_keyPressEvent_orig = self.txtSearch.keyPressEvent
        self.txtSearch.keyPressEvent = self._filter_key_press

    def _create_collection_item(self, collection_name: str) -> QtWidgets.QTreeWidgetItem:
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, collection_name)
        item.setData(0, self.ROLE_TOOL_CLASS, None)
        item.setData(0, self.ROLE_ITEM_TYPE, self.ITEM_TYPE_COLLECTION)
        return item

    def _create_tool_item(self, tool_class: Type[xappt.BaseTool]) -> QtWidgets.QTreeWidgetItem:
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, tool_class.name())
        item.setToolTip(0, tool_class.help())
        item.setData(0, self.ROLE_TOOL_CLASS, tool_class)
        item.setData(0, self.ROLE_ITEM_TYPE, self.ITEM_TYPE_TOOL)
        return item

    def populate_plugins(self):
        self.treeTools.clear()
        plugin_list: DefaultDict[str, List[Type[xappt.BaseTool]]] = defaultdict(list)

        for _, plugin_class in xappt.plugin_manager.registered_tools():
            collection = plugin_class.collection()
            plugin_list[collection].append(plugin_class)

        for collection in sorted(plugin_list.keys(), key=lambda x: x.lower()):
            collection_item = self._create_collection_item(collection)
            self.treeTools.insertTopLevelItem(self.treeTools.topLevelItemCount(), collection_item)
            for plugin in sorted(plugin_list[collection], key=lambda x: x.name().lower()):
                tool_item = self._create_tool_item(plugin)
                collection_item.addChild(tool_item)
            collection_item.setExpanded(True)

    def item_activated(self, item: QtWidgets.QTreeWidgetItem, column: int):
        item_type = item.data(column, self.ROLE_ITEM_TYPE)
        if item_type != self.ITEM_TYPE_TOOL:
            return
        tool_class: Type[xappt.BaseTool] = item.data(column, self.ROLE_TOOL_CLASS)
        if self.chkLaunchNewProcess.isChecked():
            self.launch_tool_new_process(tool_class)
        else:
            self.launch_tool(tool_class)

    @staticmethod
    def launch_command(tool_name: str) -> Tuple:
        return sys.executable, "-m", "xappt_qt.launcher", tool_name

    def launch_tool(self, tool_class: Type[xappt.BaseTool]):
        interface = xappt.get_interface()
        tool_instance = tool_class(interface=interface)
        interface.invoke(tool_instance)

    def launch_tool_new_process(self, tool_class: Type[xappt.BaseTool]):
        tool_name = tool_class.name()
        launch_command = self.launch_command(tool_name)
        if platform.system() == "Windows":
            proc = subprocess.Popen(launch_command, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            proc = subprocess.Popen(launch_command)
        print(f"Launched process {proc.pid}")

    def selection_changed(self):
        help_text = ""
        selected_items = self.treeTools.selectedItems()
        if len(selected_items):
            tool_class = selected_items[0].data(0, self.ROLE_TOOL_CLASS)  # type: xappt.BaseTool
            if tool_class is not None and len(tool_class.help()):
                help_text = f"{tool_class.name()}: {tool_class.help()}"
        self.labelHelp.setText(help_text)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save_settings()
        super().closeEvent(event)
        QtWidgets.QApplication.instance().quit()

    def _filter_key_press(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self.txtSearch.clear()
        self.__txtSearch_keyPressEvent_orig(event)

    def on_filter_tools(self, text: str):
        if len(text) == 0:
            # noinspection PyTypeChecker
            iterator = QtWidgets.QTreeWidgetItemIterator(self.treeTools, QtWidgets.QTreeWidgetItemIterator.All)
            while iterator.value():
                item = iterator.value()
                item.setHidden(False)
                iterator += 1
            return
        search_terms = [item.lower() for item in text.split(" ") if len(item)]
        self._filter_branch(search_terms, self.treeTools.invisibleRootItem())

    def _filter_branch(self, search_terms: List[str], parent: QtWidgets.QTreeWidgetItem) -> int:
        visible_children = 0
        for c in range(parent.childCount()):
            child = parent.child(c)
            item_type = child.data(0, self.ROLE_ITEM_TYPE)
            if item_type == self.ITEM_TYPE_TOOL:
                child_text = child.text(0).lower()
                child_help = child.toolTip(0).lower()
                visible_children += 1
                item_hidden = False
                for term in search_terms:
                    if term not in child_text and term not in child_help:
                        item_hidden = True
                        break
                child.setHidden(item_hidden)
                if item_hidden:
                    visible_children -= 1
            elif item_type == self.ITEM_TYPE_COLLECTION:
                visible_children += self._filter_branch(search_terms, child)
            else:
                raise NotImplementedError
        parent.setHidden(visible_children == 0)
        return visible_children


def center_window(window: QtWidgets.QMainWindow, screen: Optional[QtGui.QScreen] = None):
    if screen is None:
        app = QtWidgets.QApplication.instance()
        cursor_pos = QtGui.QCursor.pos()
        screen = app.screenAt(cursor_pos)

    screen_rect = screen.availableGeometry()
    window_rect = QtCore.QRect(QtCore.QPoint(0, 0), window.frameSize().boundedTo(screen_rect.size()))
    window.resize(window_rect.size())
    window.move(screen_rect.center() - window_rect.center())


def main(args) -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(args)
    apply_palette(app)

    browser = XapptBrowser()
    center_window(browser)
    browser.show()

    app.setProperty(APP_PROPERTY_RUNNING, True)
    return app.exec_()


def entry_point() -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME
    return main(sys.argv)


if __name__ == '__main__':
    sys.exit(entry_point())
