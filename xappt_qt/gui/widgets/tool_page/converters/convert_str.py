import webbrowser

from PyQt5 import QtWidgets, QtCore

import xappt

from xappt_qt.gui.widgets.tool_page.converters.base import ParameterWidgetBase
from xappt_qt.gui.widgets.file_edit import FileEdit
from xappt_qt.gui.widgets.text_edit import TextEdit
from xappt_qt.gui.widgets.table_edit import TableEdit
from xappt_qt.utilities.text import to_markdown


class ParameterWidgetStr(ParameterWidgetBase):
    def get_widget(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            return self._convert_str_choice(param)
        else:
            return self._convert_str_edit(param)

    def _convert_str_choice(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QComboBox()
        w.addItems(param.choices)
        for v in (param.value, param.default):
            if v is not None and v in param.choices:
                index = w.findText(v)
                w.setCurrentIndex(index)
                break
        else:
            param.value = w.currentText()

        self._setup_combobox(param, w)

        w.currentIndexChanged[str].connect(lambda x: self.onValueChanged.emit(param.name, x))

        self._getter_fn = w.currentText
        self._setter_fn = lambda s, widget=w: widget.setCurrentIndex(widget.findText(s))

        return w

    def _convert_str_edit(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        ui = param.options.get("ui")
        if ui == "folder-select":
            w = FileEdit(mode=FileEdit.MODE_CHOOSE_DIR)
            w.onSetFile.connect(lambda x: self.onValueChanged.emit(param.name, x))
        elif ui == "file-open":
            w = FileEdit(accept=param.options.get("accept"), mode=FileEdit.MODE_OPEN_FILE)
            w.onSetFile.connect(lambda x: self.onValueChanged.emit(param.name, x))
        elif ui == "file-save":
            w = FileEdit(accept=param.options.get("accept"), mode=FileEdit.MODE_SAVE_FILE)
            w.onSetFile.connect(lambda x: self.onValueChanged.emit(param.name, x))
        elif ui == "multi-line":
            w = TextEdit()
            w.editingFinished.connect(lambda widget=w: self.onValueChanged.emit(param.name, widget.text()))
        elif ui in ("label", "markdown"):
            w = QtWidgets.QLabel()
            w.setTextFormat(QtCore.Qt.RichText)
            w.setWordWrap(True)
            self.caption = ""
            w.linkActivated.connect(self.link_activated)
        elif ui == "csv":
            w = TableEdit(header_row=param.options.get("header_row", False),
                          editable=param.options.get("editable", False),
                          csv_import=param.options.get("csv_import", False),
                          csv_export=param.options.get("csv_export", True),
                          sorting_enabled=param.options.get("sorting_enabled", True))
            w.data_changed.connect(lambda widget=w: self.onValueChanged.emit(param.name, widget.text()))
        else:
            w = QtWidgets.QLineEdit()
            if ui == "password":
                w.setEchoMode(QtWidgets.QLineEdit.Password)
            w.editingFinished.connect(lambda widget=w: self.onValueChanged.emit(param.name, widget.text()))

        self._getter_fn = w.text
        if ui == "markdown":
            self._setter_fn = lambda t, widget=w: w.setText(to_markdown(t))
        else:
            self._setter_fn = w.setText

        for v in (param.value, param.default):
            if v is not None:
                self._setter_fn(v)
                break
        else:
            self._setter_fn("")

        return w

    @staticmethod
    def link_activated(url: str):
        webbrowser.open(url)
