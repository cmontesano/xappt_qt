from typing import Generator, List, Sequence

from PyQt5 import QtCore, QtWidgets

from xappt_qt.gui.delegates import SimpleItemDelegate


class CheckList(QtWidgets.QListWidget):
    item_changed = QtCore.pyqtSignal(QtWidgets.QListWidgetItem)

    def __init__(self):
        super().__init__()
        self.setItemDelegate(SimpleItemDelegate())
        # noinspection PyUnresolvedReferences
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setSpacing(2)
        self.itemChanged.connect(self._on_item_changed)

        self._init_context_menu()

    def _init_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.context_menu = QtWidgets.QMenu()

        action_check = QtWidgets.QAction("Check All", self)
        action_check.setData(self.check_all)
        self.context_menu.addAction(action_check)

        action_uncheck = QtWidgets.QAction("Check None", self)
        action_uncheck.setData(self.uncheck_all)
        self.context_menu.addAction(action_uncheck)

        action_selected = QtWidgets.QAction("Check Selected", self)
        action_selected.setData(self.check_selected)
        self.context_menu.addAction(action_selected)

        action_invert = QtWidgets.QAction("Invert Checked", self)
        action_invert.setData(self.invert_checked)
        self.context_menu.addAction(action_invert)

        self.customContextMenuRequested.connect(self._on_context_menu)

    def addItem(self, *args, **kwargs):
        raise NotImplementedError

    def addItems(self, *args, **kwargs):
        raise NotImplementedError

    def add_item(self, text: str, state: QtCore.Qt.CheckState = QtCore.Qt.Unchecked):
        item = QtWidgets.QListWidgetItem(text)
        # noinspection PyTypeChecker
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(state)
        super().addItem(item)

    def add_items(self, items: Sequence[str], state: QtCore.Qt.CheckState = QtCore.Qt.Unchecked):
        for item in items:
            self.add_item(item, state)

    def checked_items(self) -> Generator[str, None, None]:
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                yield item.text()

    def check_all(self):
        self._set_check_state(QtCore.Qt.Checked)

    def uncheck_all(self):
        self._set_check_state(QtCore.Qt.Unchecked)

    def invert_checked(self):
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)

    def check_selected(self):
        for i in range(self.count()):
            item = self.item(i)
            if item.isSelected():
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def check_items(self, items: Sequence[str]):
        for item in items:
            for match in self.findItems(item, QtCore.Qt.MatchExactly):
                match.setCheckState(QtCore.Qt.Checked)

    def _set_check_state(self, state: QtCore.Qt.CheckState):
        for i in range(self.count()):
            self.item(i).setCheckState(state)

    def _on_item_changed(self, item: QtWidgets.QListWidgetItem):
        self.item_changed.emit(item)

    def _on_context_menu(self, pos: QtCore.QPoint):
        if len(self.context_menu.actions()) == 0:
            return
        action = self.context_menu.exec_(self.mapToGlobal(pos))
        if action is None:
            return
        action_fn = action.data()
        action_fn()
