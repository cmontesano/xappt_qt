from typing import Callable, Optional

from PyQt5 import QtCore, QtWidgets

import xappt


class ParameterWidgetBase(QtWidgets.QWidget):
    onValueChanged = QtCore.pyqtSignal(str, object)  # param name, param value

    def __init__(self, *, parameter: xappt.Parameter, parent: Optional[QtWidgets.QWidget]):
        super().__init__(parent=parent)

        self.caption = self._get_caption(parameter)
        self._getter_fn: Optional[Callable] = None
        self._setter_fn: Optional[Callable] = None

        w = self.get_widget(parameter)

        self.setSizePolicy(w.sizePolicy())
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(w)

        parameter.metadata['ui-setter'] = self._setter_fn

    @property
    def value(self):
        return self._getter_fn()

    @value.setter
    def value(self, value):
        self._setter_fn(value)

    def get_widget(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        raise NotImplementedError

    @staticmethod
    def _get_caption(param: xappt.Parameter) -> str:
        caption_default = param.name.replace("_", " ").title()
        caption = param.options.get("caption", caption_default)
        return caption

    @staticmethod
    def _setup_combobox(param: xappt.Parameter, combo_widget: QtWidgets.QComboBox):
        if param.options.get("searchable"):
            combo_widget.setEditable(True)
            combo_widget.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
            combo_widget.lineEdit().editingFinished.connect(
                lambda: combo_widget.setCurrentIndex(combo_widget.findText(combo_widget.currentText())))
            completer = combo_widget.completer()
            completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            completer.popup().setAlternatingRowColors(True)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setFilterMode(QtCore.Qt.MatchContains)
