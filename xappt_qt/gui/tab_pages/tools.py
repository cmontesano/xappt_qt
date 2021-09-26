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


class ToolList(QtWidgets.QListWidget):
    height_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setItemDelegate(SimpleItemDelegate())
        self.setUniformItemSizes(True)
        self._view_mode: ToolViewType = ToolViewType.VIEW_LIST
        self.view_mode = self._view_mode
        self._last_height = 0

    @property
    def view_mode(self) -> ToolViewType:
        return self._view_mode

    @view_mode.setter
    def view_mode(self, new_mode: ToolViewType):
        self._view_mode = new_mode
        if new_mode == ToolViewType.VIEW_LIST:
            self.setViewMode(self.ListMode)
            self.updateGeometries()
            self.updateGeometry()
            self.setWrapping(False)
            self.setResizeMode(self.Fixed)
            self.setIconSize(QtCore.QSize(24, 24))
            self.setAlternatingRowColors(True)
        else:
            self.setViewMode(self.IconMode)
            self.updateGeometries()
            self.updateGeometry()
            self.setWrapping(True)
            self.setResizeMode(self.Adjust)
            self.setAlternatingRowColors(False)
            if new_mode == ToolViewType.VIEW_ICONS_SMALL:
                self.setIconSize(QtCore.QSize(32, 32))
            elif new_mode == ToolViewType.VIEW_ICONS_LARGE:
                self.setIconSize(QtCore.QSize(64, 64))
            elif new_mode == ToolViewType.VIEW_ICONS_HUGE:
                self.setIconSize(QtCore.QSize(92, 92))

    def add_plugin(self, tool_class: Type[xappt.BaseTool]):
        item = QtWidgets.QListWidgetItem()
        item.setText(tool_class.name())
        item.setToolTip(help_text(tool_class, process_markdown=True, include_name=True))
        item.setData(ToolItemDelegate.ROLE_TOOL_CLASS, tool_class)
        item.setData(ToolItemDelegate.ROLE_ITEM_TYPE, ToolItemDelegate.ITEM_TYPE_TOOL)
        item.setData(ToolItemDelegate.ROLE_ITEM_SEARCH_TEXT, f'{tool_class.name()}\n{tool_class.help()}')
        icon_path = get_tool_icon(tool_class)
        item.setIcon(QtGui.QIcon(str(icon_path)))
        self.addItem(item)
        self.recalc_size()

    def recalc_size(self):
        visible_count = len(list(self.visible_items()))
        if visible_count == 0:
            return
        item_rect = self.visualItemRect(self.item(0))
        if self.view_mode == ToolViewType.VIEW_LIST:
            columns = 1
        else:
            columns = self.contentsRect().width() // (item_rect.width() + 2)
        rows = int(math.ceil(visible_count / columns))
        row_size = self.sizeHintForRow(0)
        frame_size = 4
        new_height = (row_size * rows) + frame_size
        if new_height == self._last_height:
            return
        self.setMinimumHeight(new_height)
        self._last_height = new_height
        self.height_changed.emit()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        self.recalc_size()

    def visible_items(self) -> Generator[QtWidgets.QListWidgetItem, None, None]:
        for item in self.all_items():
            if not item.isHidden():
                yield item

    def all_items(self) -> Generator[QtWidgets.QListWidgetItem, None, None]:
        for i in range(self.count()):
            yield self.item(i)

    def unhide_all(self):
        for item in self.all_items():
            item.setHidden(False)


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
            list_widget = self._create_plugin_list(collection_item)

            for plugin in sorted(plugin_list[collection], key=lambda x: x.name().lower()):
                list_widget.add_plugin(plugin)
                self.loaded_plugins[collection].append(plugin)

            collection_item.setExpanded(True)

    def connect_signals(self):
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

    def _create_plugin_list(self, parent: QtWidgets.QTreeWidgetItem) -> ToolList:
        child_item = QtWidgets.QTreeWidgetItem()
        parent.addChild(child_item)
        list_widget = ToolList()
        self.treeTools.setItemWidget(child_item, 0, list_widget)
        list_widget.height_changed.connect(lambda: child_item.setHidden(False))
        list_widget.itemActivated.connect(self.item_activated)
        list_widget.itemSelectionChanged.connect(lambda w=list_widget: self.selection_changed(w))
        child_item.setData(0, ToolItemDelegate.ROLE_ITEM_TYPE, ToolItemDelegate.ITEM_TYPE_TOOL)
        child_item.setData(0, ToolItemDelegate.ROLE_ITEM_LIST, list_widget)
        return list_widget

    def item_activated(self, item: QtWidgets.QListWidgetItem):
        item_type = item.data(ToolItemDelegate.ROLE_ITEM_TYPE)
        if item_type != ToolItemDelegate.ITEM_TYPE_TOOL:
            return
        tool_class: Type[xappt.BaseTool] = item.data(ToolItemDelegate.ROLE_TOOL_CLASS)
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

    def selection_changed(self, list_widget: QtWidgets.QListWidget):
        selected_items = list_widget.selectedItems()
        if len(selected_items):
            self.labelHelp.setText(selected_items[0].toolTip())
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
                if item.data(0, ToolItemDelegate.ROLE_ITEM_TYPE) == ToolItemDelegate.ITEM_TYPE_TOOL:
                    list_widget: ToolList = item.data(0, ToolItemDelegate.ROLE_ITEM_LIST)
                    list_widget.unhide_all()
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
                list_widget: ToolList = child.data(0, ToolItemDelegate.ROLE_ITEM_LIST)
                for item in list_widget.all_items():
                    search_text = item.data(ToolItemDelegate.ROLE_ITEM_SEARCH_TEXT)
                    visible_children += 1
                    item_hidden = False
                    for term in search_terms:
                        if term not in search_text:
                            item_hidden = True
                            break
                    item.setHidden(item_hidden)
                    if item_hidden:
                        visible_children -= 1
                list_widget.recalc_size()
            elif item_type == ToolItemDelegate.ITEM_TYPE_COLLECTION:
                visible_children += self._filter_branch(search_terms, child)
            else:
                raise NotImplementedError
        parent.setHidden(visible_children == 0)
        return visible_children

    @staticmethod
    def on_link_activated(url: str):
        webbrowser.open(url)
