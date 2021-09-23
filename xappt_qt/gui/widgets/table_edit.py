import csv

from typing import Optional

from PyQt5 import QtWidgets, QtCore


class CsvTextCapture:
    def __init__(self):
        self.rows = []

    def write(self, row: str):
        self.rows.append(row)


class TableEdit(QtWidgets.QTableWidget):
    data_changed = QtCore.pyqtSignal()

    COMMAND_INS_BEFORE = "Insert Before"
    COMMAND_INS_AFTER = "Insert After"
    COMMAND_DELETE = "Delete"
    COMMAND_RENAME = "Rename"

    def __init__(self, **kwargs):
        parent: Optional[QtWidgets.QWidget] = kwargs.get("parent")
        super().__init__(parent=parent)

        self._editable: bool = kwargs.get("editable", False)
        self._header_row: bool = kwargs.get("header_row", False)

        self.setup_table()
        self._first_load = True

    def setup_table(self):
        self.setAlternatingRowColors(True)
        if not self._editable:
            self.setEditTriggers(self.NoEditTriggers)
        else:
            self._init_context_menu()

        self.itemChanged.connect(self.on_data_changed)

    def on_data_changed(self, _: QtWidgets.QTableWidgetItem):
        self.data_changed.emit()

    def _init_context_menu(self):
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self._on_context_menu_header_h)

        self.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self._on_context_menu_header_v)

    def _on_context_menu_header_h(self, pos: QtCore.QPoint):
        column = self.columnAt(pos.x())
        self.selectColumn(column)

        menu_header = QtWidgets.QMenu()
        for action_name in (self.COMMAND_INS_BEFORE, self.COMMAND_INS_AFTER, self.COMMAND_DELETE, self.COMMAND_RENAME):
            action = QtWidgets.QAction(action_name, self)
            menu_header.addAction(action)

        action = menu_header.exec_(self.horizontalHeader().mapToGlobal(pos))
        if action is None:
            return
        if action.text() == self.COMMAND_INS_BEFORE:
            self.insertColumn(column)
        elif action.text() == self.COMMAND_INS_AFTER:
            self.insertColumn(column + 1)
        elif action.text() == self.COMMAND_DELETE:
            self.removeColumn(column)
        elif action.text() == self.COMMAND_RENAME:
            item = self.horizontalHeaderItem(column)
            if item is not None:
                current_name = item.text()
            else:
                current_name = ""
            new_name, success = QtWidgets.QInputDialog.getText(self, "Rename", "Rename Column", text=current_name)
            if success and len(new_name.strip()):
                self.horizontalHeaderItem(column).setText(new_name)
        else:
            return
        self.data_changed.emit()

    def _on_context_menu_header_v(self, pos: QtCore.QPoint):
        row = self.rowAt(pos.y())
        self.selectRow(row)

        menu_header = QtWidgets.QMenu()
        for action_name in (self.COMMAND_INS_BEFORE, self.COMMAND_INS_AFTER, self.COMMAND_DELETE):
            action = QtWidgets.QAction(action_name, self)
            menu_header.addAction(action)

        action = menu_header.exec_(self.verticalHeader().mapToGlobal(pos))
        if action is None:
            return
        if action.text() == self.COMMAND_INS_BEFORE:
            self.insertRow(row)
        elif action.text() == self.COMMAND_INS_AFTER:
            self.insertRow(row + 1)
        elif action.text() == self.COMMAND_DELETE:
            self.removeRow(row)
        else:
            return
        self.data_changed.emit()

    # noinspection PyPep8Naming
    def setText(self, source: str):
        self.blockSignals(True)
        reader = csv.reader(source.splitlines())

        rows = []
        column_count = 0
        for row in reader:
            rows.append(row)
            column_count = max(len(row), column_count)

        if column_count > 0 and len(rows):
            headers = rows.pop(0) if self._header_row else None

            self.setColumnCount(column_count)
            self.setRowCount(len(rows))
            if headers is not None:
                self.setHorizontalHeaderLabels(headers)

            for r, row in enumerate(rows):
                for c, text in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(text)
                    self.setItem(r, c, item)

        if self._first_load:
            self.resizeColumnsToContents()
            self._first_load = False

        self.blockSignals(False)

    def text(self) -> str:
        rows = []

        if self._header_row:
            header_row = []
            for column in range(self.columnCount()):
                item = self.horizontalHeaderItem(column)
                if item is None:
                    header_row.append("")
                else:
                    header_row.append(item.text())
            rows.append(header_row)

        for row in range(self.rowCount()):
            this_row = []
            for column in range(self.columnCount()):
                item = self.item(row, column)
                if item is not None:
                    this_row.append(item.text())
                else:
                    this_row.append("")
            rows.append(this_row)

        csv_capture = CsvTextCapture()
        csv.writer(csv_capture).writerows(rows)

        return "".join(csv_capture.rows)
