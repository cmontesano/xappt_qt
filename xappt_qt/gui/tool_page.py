from typing import Any, Callable, Dict, List, Optional, Type

from PySide2 import QtWidgets, QtCore

import xappt

from xappt_qt.gui.widgets import *
from xappt_qt.gui.delegates import SimpleItemDelegate


class ToolPage(QtWidgets.QWidget):
    def __init__(self, tool: xappt.BaseTool, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.convert_dispatch: Dict[Type, Callable] = {
            int: self._convert_int,
            bool: self._convert_bool,
            float: self._convert_float,
            str: self._convert_str,
            list: self._convert_list,
        }

        self.tool = tool
        self.build_ui()

    # noinspection PyAttributeOutsideInit
    def build_ui(self):
        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(8)

        self.setLayout(self.grid)
        self._load_tool_parameters()

    @staticmethod
    def get_caption(param: xappt.Parameter) -> str:
        caption_default = param.name.replace("_", " ").title()
        caption = param.options.get("caption", caption_default)
        return caption

    def update_tool_choices(self, param: xappt.Parameter):
        """ Given that multiple parameter types can be updated at runtime,
        it's easier just to remove and recreate the widget rather than
        reimplementing a lot of the same functionality to update existing
        widgets. """
        widget = param.metadata.get('widget')
        if widget is None:
            return

        # find and remove existing widget
        index = self.grid.indexOf(widget)
        row, column, *_ = self.grid.getItemPosition(index)
        self.grid.takeAt(index)
        widget.deleteLater()
        param.on_choices_changed.clear()

        # create a new widget to replace it
        new_widget = self.convert_parameter(param)
        self.grid.addWidget(new_widget, row, column)
        param.metadata['widget'] = new_widget
        param.on_choices_changed.add(self.update_tool_choices)

    def _load_tool_parameters(self):
        for i, param in enumerate(self.tool.parameters()):
            label = QtWidgets.QLabel(self.get_caption(param))
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            label.setToolTip(param.description)
            widget = self.convert_parameter(param)
            widget.setToolTip(param.description)
            self.grid.addWidget(label, i, 0)
            self.grid.addWidget(widget, i, 1)
            param.metadata['label'] = label
            param.metadata['widget'] = widget  # this lets us avoid lambdas
            param.on_choices_changed.add(self.update_tool_choices)
            param.on_value_changed.add(self.widget_value_updated)
            param.on_options_changed.add(self.widget_options_updated)

    def convert_parameter(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        convert_fn = self.convert_dispatch.get(param.data_type)
        if convert_fn is not None:
            return convert_fn(param)
        return QtWidgets.QWidget()

    def _convert_int(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            return self._convert_int_choice(param)
        else:
            return self._convert_int_spin(param)

    def _convert_int_choice(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QComboBox()
        w.addItems(param.choices)
        for v in (param.value, param.default):
            if v is not None:
                if isinstance(v, str):
                    if v in param.choices:
                        index = w.findText(v)
                        w.setCurrentIndex(index)
                elif isinstance(v, int):
                    if 0 <= v < w.count():
                        w.setCurrentIndex(v)
                break
        else:
            param.value = w.currentIndex()
        w.currentIndexChanged[int].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = w.setCurrentIndex
        return w

    def _convert_int_spin(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QSpinBox(parent=self)
        minimum = param.options.get("minimum", -999999999)
        maximum = param.options.get("maximum", 999999999)
        w.setMinimum(minimum)
        w.setMaximum(maximum)
        for v in (param.value, param.default):
            if v is not None:
                w.setValue(v)
                break
        else:
            param.value = w.value()
        w.valueChanged[int].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = w.setValue
        return w

    def _convert_bool(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QCheckBox()
        for v in (param.value, param.default):
            if v is not None:
                w.setChecked(v)
                break
        else:
            param.value = w.isChecked()
        w.stateChanged.connect(lambda x: self.update_tool_param(param.name, x == QtCore.Qt.Checked))
        param.metadata['ui-setter'] = w.setChecked
        return w

    def _convert_str(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            return self._convert_str_choice(param)
        else:
            return self._convert_str_edit(param)

    def _convert_str_choice(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QComboBox()
        w.addItems(param.choices)
        for v in (param.value, param.default):
            if v is not None:
                if v in param.choices:
                    index = w.findText(param.default)
                    w.setCurrentIndex(index)
                    break
        else:
            param.value = w.currentText()
        w.currentIndexChanged[str].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = lambda s, widget=w: widget.setCurrentIndex(widget.findText(s))
        return w

    def _convert_str_edit(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        ui = param.options.get("ui")
        if ui == "folder-select":
            w = FileEdit(mode=FileEdit.MODE_CHOOSE_DIR)
            w.onSetFile.connect(lambda x: self.update_tool_param(param.name, x))
        elif ui == "file-open":
            w = FileEdit(accept=param.options.get("accept"), mode=FileEdit.MODE_OPEN_FILE)
            w.onSetFile.connect(lambda x: self.update_tool_param(param.name, x))
        elif ui == "file-save":
            w = FileEdit(accept=param.options.get("accept"), mode=FileEdit.MODE_SAVE_FILE)
            w.onSetFile.connect(lambda x: self.update_tool_param(param.name, x))
        else:
            w = QtWidgets.QLineEdit()
            w.textChanged.connect(lambda x: self.update_tool_param(param.name, x))

        for v in (param.value, param.default):
            if v is not None:
                w.setText(param.value)
                break
        else:
            w.setText("")
        param.metadata['ui-setter'] = w.setText
        return w

    # noinspection DuplicatedCode
    def _convert_float(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QDoubleSpinBox(parent=self)
        minimum = param.options.get("minimum", -999999999.0)
        maximum = param.options.get("maximum", 999999999.0)
        w.setMinimum(minimum)
        w.setMaximum(maximum)
        if param.default is not None:
            w.setValue(param.default)
        param.value = w.value()
        w.valueChanged[float].connect(lambda x: self.update_tool_param(param.name, x))
        param.metadata['ui-setter'] = w.setValue
        return w

    def _convert_list(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QListWidget()
        w.setItemDelegate(SimpleItemDelegate())
        w.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        w.setAlternatingRowColors(True)
        w.setSpacing(2)
        if param.choices is not None:
            w.addItems(param.choices)
        for v in (param.value, param.default):
            if v is not None:
                for item in v:
                    for match in w.findItems(item, QtCore.Qt.MatchExactly):
                        match.setSelected(True)
                break
        param.value = self._get_selected_list_items(w)
        w.itemSelectionChanged.connect(lambda: self.update_list_param(param.name))
        param.metadata['ui-setter'] = lambda value, widget=w: self.set_list_value(value, widget)
        return w

    @staticmethod
    def _get_selected_list_items(widget: QtWidgets.QListWidget) -> List[str]:
        return [item.text() for item in widget.selectedItems()]

    def update_list_param(self, name: str):
        param: xappt.Parameter = getattr(self.tool, name)
        widget: QtWidgets.QListWidget = param.metadata.get('widget')
        if widget is None:
            return
        selected_items = self._get_selected_list_items(widget)
        param.on_value_changed.paused = True
        param.value = param.validate(selected_items)
        param.on_value_changed.paused = False

    def update_tool_param(self, name: str, value: Any):
        param: xappt.Parameter = getattr(self.tool, name)
        param.value = param.validate(value)

    @staticmethod
    def set_list_value(items: List[str], widget: QtWidgets.QListWidget):
        for item in items:
            for match in widget.findItems(item, QtCore.Qt.MatchExactly):
                match.setSelected(True)

    @staticmethod
    def widget_value_updated(param: xappt.Parameter):
        setter = param.metadata.get('ui-setter')
        if setter is None:
            return
        setter(param.value)

    @staticmethod
    def widget_options_updated(param: xappt.Parameter):
        label: Optional[QtWidgets.QLabel] = param.metadata.get('label')
        widget: Optional[QtWidgets.QWidget] = param.metadata.get('widget')

        visible = param.option("visible", True)
        if label is not None:
            label.setVisible(visible)
        if widget is not None:
            widget.setVisible(visible)

        enabled = param.option("enabled", True)
        if widget is not None:
            widget.setEnabled(enabled)
