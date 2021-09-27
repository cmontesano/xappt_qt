import importlib.resources
import math
import platform
import subprocess
import sys
import webbrowser

from PyQt5 import QtWidgets, QtGui, QtCore

from collections import defaultdict
from typing import DefaultDict, Generator, List, Tuple

import xappt

import xappt_qt
import xappt_qt.config
from xappt_qt.constants import APP_TITLE, ToolViewType
from xappt_qt.gui.ui.browser_tab_tools import Ui_tabTools
from xappt_qt.gui.delegates import SimpleItemDelegate, ToolItemDelegate
from xappt_qt.gui.tab_pages.base import BaseTabPage
from xappt_qt.utilities.tool_attributes import *


ICON_SIZES = {
    ToolViewType.VIEW_SMALL_ICONS: QtCore.QSize(24, 24),
    ToolViewType.VIEW_LARGE_ICONS: QtCore.QSize(48, 48),
}


class ToolsTabPage(BaseTabPage, Ui_tabTools):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setupUi(self)

        self.set_tree_attributes()

        with importlib.resources.path("xappt_qt.resources.icons", "clear.svg") as path:
            self.btnClear.setIcon(QtGui.QIcon(str(path)))

        self.loaded_plugins: DefaultDict[str, List[Type[xappt.BaseTool]]] = defaultdict(list)
        self.populate_plugins()
        self.connect_signals()

    def set_tree_attributes(self):
        self.treeTools.setIconSize(QtCore.QSize(24, 24))
        self.treeTools.setItemDelegate(ToolItemDelegate())

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
                self.loaded_plugins[collection].append(plugin)
            collection_item.setExpanded(True)

    def connect_signals(self):
        self.treeTools.itemActivated.connect(self.item_activated)
        self.treeTools.itemSelectionChanged.connect(self.selection_changed)
        self.treeTools.clicked.connect(self.on_tree_item_clicked)

        self.txtSearch.textChanged.connect(self.on_filter_tools)
        # noinspection PyAttributeOutsideInit
        self.__txtSearch_keyPressEvent_orig = self.txtSearch.keyPressEvent
        self.txtSearch.keyPressEvent = self._filter_key_press

        self.labelHelp.linkActivated.connect(self.on_link_activated)

    def on_tree_item_clicked(self, index: QtCore.QModelIndex):
        if index.data(ToolItemDelegate.ROLE_ITEM_TYPE) != ToolItemDelegate.ITEM_TYPE_COLLECTION:
            return
        if self.treeTools.isExpanded(index):
            self.treeTools.collapse(index)
        else:
            self.treeTools.expand(index)

    @staticmethod
    def _create_collection_item(collection_name: str) -> QtWidgets.QTreeWidgetItem:
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, collection_name)
        item.setData(0, ToolItemDelegate.ROLE_TOOL_CLASS, None)
        item.setData(0, ToolItemDelegate.ROLE_ITEM_TYPE, ToolItemDelegate.ITEM_TYPE_COLLECTION)
        return item

    @staticmethod
    def _create_tool_item(tool_class: Type[xappt.BaseTool]) -> QtWidgets.QTreeWidgetItem:
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, tool_class.name())
        item.setToolTip(0, help_text(tool_class, process_markdown=True, include_name=True))
        item.setData(0, ToolItemDelegate.ROLE_TOOL_CLASS, tool_class)
        item.setData(0, ToolItemDelegate.ROLE_ITEM_TYPE, ToolItemDelegate.ITEM_TYPE_TOOL)
        item.setData(0, ToolItemDelegate.ROLE_ITEM_SEARCH_TEXT, f'{tool_class.name()}\n{tool_class.help()}')

        icon_path = get_tool_icon(tool_class)
        item.setIcon(0, QtGui.QIcon(str(icon_path)))

        return item

    def item_activated(self, item: QtWidgets.QTreeWidgetItem, column: int):
        item_type = item.data(column, ToolItemDelegate.ROLE_ITEM_TYPE)
        if item_type != ToolItemDelegate.ITEM_TYPE_TOOL:
            return
        tool_class: Type[xappt.BaseTool] = item.data(column, ToolItemDelegate.ROLE_TOOL_CLASS)
        self.launch_tool(tool_class)

    @staticmethod
    def launch_command(tool_name: str) -> Tuple:
        if xappt_qt.executable is not None:
            return xappt_qt.executable, tool_name
        return sys.executable, "-m", "xappt_qt.launcher", tool_name

    def launch_tool(self, tool_class: Type[xappt.BaseTool]):
        tool_name = tool_class.name()
        try:
            launch_command = self.launch_command(tool_name)
        except TypeError:
            self.critical(APP_TITLE, "Could not find executable")
        else:
            if platform.system() == "Windows":
                proc = subprocess.Popen(launch_command, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                proc = subprocess.Popen(launch_command)
            self.information(APP_TITLE, f"Launched {tool_name} (pid {proc.pid})")

    def selection_changed(self):
        selected_items = self.treeTools.selectedItems()
        if len(selected_items):
            self.labelHelp.setText(selected_items[0].toolTip(0))
        else:
            self.labelHelp.setText("")

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
            item_type = child.data(0, ToolItemDelegate.ROLE_ITEM_TYPE)
            if item_type == ToolItemDelegate.ITEM_TYPE_TOOL:
                search_text = child.data(0, ToolItemDelegate.ROLE_ITEM_SEARCH_TEXT)
                visible_children += 1
                item_hidden = False
                for term in search_terms:
                    if term not in search_text:
                        item_hidden = True
                        break
                child.setHidden(item_hidden)
                if item_hidden:
                    visible_children -= 1
            elif item_type == ToolItemDelegate.ITEM_TYPE_COLLECTION:
                visible_children += self._filter_branch(search_terms, child)
            else:
                raise NotImplementedError
        parent.setHidden(visible_children == 0)
        return visible_children

    @staticmethod
    def on_link_activated(url: str):
        webbrowser.open(url)

    def settings_changed(self, settings: dict):
        view_type = settings.get('view_type', 0)
        self.treeTools.setIconSize(ICON_SIZES[view_type])

        # noinspection PyTypeChecker
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeTools, QtWidgets.QTreeWidgetItemIterator.All)
        while iterator.value():
            item = iterator.value()
            if item.data(0, ToolItemDelegate.ROLE_ITEM_TYPE) == ToolItemDelegate.ITEM_TYPE_TOOL:
                item.setData(0, ToolItemDelegate.ROLE_ICON_SIZE, ICON_SIZES[view_type])
            else:
                item.setData(0, ToolItemDelegate.ROLE_ICON_SIZE, ICON_SIZES[ToolViewType.VIEW_SMALL_ICONS])
            iterator += 1
