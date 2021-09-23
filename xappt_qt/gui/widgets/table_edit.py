import csv
import pathlib

from typing import Optional, Sequence

from PyQt5 import QtWidgets, QtCore, QtGui

from xappt_qt.constants import APP_TITLE


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

    COMMAND_IMPORT = "Import CSV..."
    COMMAND_EXPORT = "Export CSV..."

    CSV_FILTER = "CSV Files *.csv (*.csv)"
    IO_FILTERS = {  # filter text, suffix list
        CSV_FILTER: ".csv",
        "All Files * (*)": None,
    }

    def __init__(self, **kwargs):
        parent: Optional[QtWidgets.QWidget] = kwargs.get("parent")
        super().__init__(parent=parent)

        # attributes
        self._editable: bool = kwargs.get("editable", False)
        self._header_row: bool = kwargs.get("header_row", False)
        self._csv_import: bool = kwargs.get("csv_import", False)
        self._csv_export: bool = kwargs.get("csv_export", True)
        self._sorting_enabled: bool = kwargs.get("sorting_enabled", True)

        # setup
        self._init_table_attributes()
        self._init_context_menu()
        self._init_drag_and_drop()

        # state
        self._first_load = True
        self._last_path: pathlib.Path = pathlib.Path.cwd()
        self._last_filter: str = self.CSV_FILTER

        # signals
        self.itemChanged.connect(self.on_data_changed)

    def _init_table_attributes(self):
        if not self._editable:
            self.setEditTriggers(self.NoEditTriggers)

        self.setAlternatingRowColors(True)
        self.setSortingEnabled(self._sorting_enabled)

    def _init_drag_and_drop(self):
        self._acceptable_drop_suffix_list = []
        if self._csv_import:
            for suffix in self.IO_FILTERS.values():
                if isinstance(suffix, str):
                    self._acceptable_drop_suffix_list.append(suffix)
                elif isinstance(suffix, Sequence):
                    for item in suffix:
                        self._acceptable_drop_suffix_list.append(item)
            self.setAcceptDrops(True)

    def on_data_changed(self, _: QtWidgets.QTableWidgetItem):
        self.data_changed.emit()

    def _init_context_menu(self):
        if self._editable:
            self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.horizontalHeader().customContextMenuRequested.connect(self._on_context_menu_header_h)

            self.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.verticalHeader().customContextMenuRequested.connect(self._on_context_menu_header_v)

        if self._csv_import or self._csv_export:
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self._on_context_menu_table)

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

    def _on_context_menu_table(self, pos: QtCore.QPoint):
        menu_table = QtWidgets.QMenu()

        if self._csv_import:
            menu_table.addAction(QtWidgets.QAction(self.COMMAND_IMPORT, self))

        if self._csv_export:
            menu_table.addAction(QtWidgets.QAction(self.COMMAND_EXPORT, self))

        action = menu_table.exec_(self.viewport().mapToGlobal(pos))
        if action is None:
            return
        if action.text() == self.COMMAND_IMPORT:
            self.prompt_open_file()
        elif action.text() == self.COMMAND_EXPORT:
            self.export_file()

    # noinspection PyPep8Naming
    def setText(self, source: str, **kwargs):
        header_row = kwargs.get("header_row", self._header_row)

        self.blockSignals(True)
        reader = csv.reader(source.splitlines())

        self.clear()

        rows = []
        column_count = 0
        for row in reader:
            rows.append(row)
            column_count = max(len(row), column_count)

        if column_count > 0 and len(rows):
            headers = rows.pop(0) if header_row else None

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

    def text(self, **kwargs) -> str:
        rows = []

        include_headers = kwargs.get("include_headers", self._header_row)

        if include_headers:
            header_row = []
            for column in range(self.columnCount()):
                item = self.horizontalHeaderItem(column)
                header_row.append("" if item is None else item.text())
            rows.append(header_row)

        for row in range(self.rowCount()):
            this_row = []
            for column in range(self.columnCount()):
                item = self.item(row, column)
                this_row.append("" if item is None else item.text())
            rows.append(this_row)

        csv_capture = CsvTextCapture()
        csv.writer(csv_capture).writerows(rows)

        return "".join(csv_capture.rows)

    def prompt_open_file(self):
        file_name, selected_filter = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Import File', str(self._last_path), ";;".join(self.IO_FILTERS.keys()), self._last_filter)

        if len(file_name) == 0:
            return

        header_row = self.ask("Does this file include a header row?", default=True)

        path = pathlib.Path(file_name)

        self._last_filter = selected_filter
        self._last_path = path.parent

        self._read_from_file(path, header_row=header_row)

    def export_file(self):
        file_name, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Export File', str(self._last_path), ";;".join(self.IO_FILTERS.keys()), self._last_filter)

        if len(file_name) == 0:
            return

        include_headers = self.ask("Include headers in export?", default=True)

        path = pathlib.Path(file_name)

        self._last_filter = selected_filter
        self._last_path = path.parent

        suffix = self.IO_FILTERS[selected_filter]
        if suffix is None:
            # no action
            pass
        elif isinstance(suffix, str):
            if path.suffix.lower() != suffix:
                path = path.with_suffix(suffix)
        elif isinstance(suffix, Sequence):
            if path.suffix.lower() not in suffix:
                path = path.with_suffix(suffix[0])

        self._write_to_file(path, include_headers=include_headers)

        self.message(f"File saved: {path}")

    def _read_from_file(self, path: pathlib.Path, *, header_row: bool):
        if not path.is_file():
            raise FileNotFoundError(f"File does not exist: {path}")

        with path.open("r") as fp:
            contents = fp.read()

        self._first_load = True
        self.setText(contents, header_row=header_row)
        self.data_changed.emit()

    def _write_to_file(self, path: pathlib.Path, *, include_headers: bool):
        with path.open("w", newline="\n") as fp:
            fp.write(self.text(include_headers=include_headers))

    def message(self, message: str):
        QtWidgets.QMessageBox.information(self, APP_TITLE, message)

    def ask(self, message: str, *, default: bool = False) -> bool:
        if default:
            default_button = QtWidgets.QMessageBox.Yes
        else:
            default_button = QtWidgets.QMessageBox.No
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ask_result = QtWidgets.QMessageBox.question(self, APP_TITLE, message, buttons=buttons,
                                                    defaultButton=default_button)
        return ask_result == QtWidgets.QMessageBox.Yes

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        urls = event.mimeData().urls()
        if len(urls) == 0:
            return
        drag_file = pathlib.Path(urls[0].toLocalFile())
        if not drag_file.is_file():
            return
        if drag_file.suffix.lower() in self._acceptable_drop_suffix_list:
            event.accept()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        pass  # seems required for dropEvent to be called

    def dropEvent(self, event: QtGui.QDropEvent):
        urls = event.mimeData().urls()
        if len(urls) == 0:
            return
        drag_file = pathlib.Path(urls[0].toLocalFile())
        if not drag_file.is_file():
            return
        header_row = self.ask("Does this file include a header row?", default=True)
        self._read_from_file(drag_file, header_row=header_row)
