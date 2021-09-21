from PyQt5 import QtWidgets, QtCore

import xappt

from xappt_qt.gui.widgets.tool_page.converters.base import ParameterWidgetBase
from xappt_qt.gui.widgets.file_edit import FileEdit
from xappt_qt.gui.widgets.text_edit import TextEdit


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
        elif ui == "label":
            w = QtWidgets.QLabel()
            w.setTextFormat(QtCore.Qt.RichText)
            self.caption = ""
        else:
            w = QtWidgets.QLineEdit()
            w.editingFinished.connect(lambda widget=w: self.onValueChanged.emit(param.name, widget.text()))

        for v in (param.value, param.default):
            if v is not None:
                w.setText(v)
                break
        else:
            w.setText("")

        self._getter_fn = w.text
        self._setter_fn = w.setText

        return w
