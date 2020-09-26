from typing import Any, Callable, Dict, Optional, Type

from PySide2 import QtWidgets, QtCore

import xappt


class ToolPage(QtWidgets.QWidget):
    def __init__(self, tool: xappt.BaseTool, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.convert_dispatch: Dict[Type, Callable] = {
            int: self._convert_int,
            bool: self._convert_bool,
            float: self._convert_float,
            str: self._convert_str,
        }

        self.tool = tool
        self.build_ui()

    # noinspection PyAttributeOutsideInit
    def build_ui(self):
        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.setLayout(self.grid)
        self._load_tool_parameters()

    def _load_tool_parameters(self):
        for i, param in enumerate(self.tool.parameters()):
            self.grid.addWidget(QtWidgets.QLabel(param.name), i, 0)
            self.grid.addWidget(self.convert_parameter(param), i, 1)

    def convert_parameter(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        convert_fn = self.convert_dispatch.get(param.data_type)
        if convert_fn is not None:
            return convert_fn(param)
        return QtWidgets.QWidget()

    # noinspection DuplicatedCode
    def _convert_int(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            w = QtWidgets.QComboBox()
            w.addItems(param.choices)
            if param.default is not None:
                if isinstance(param.default, str):
                    if param.default in param.choices:
                        index = w.findText(param.default)
                        w.setCurrentIndex(index)
                elif isinstance(param.default, int):
                    if 0 <= param.default < w.count():
                        w.setCurrentIndex(param.default)
            param.value = w.currentIndex()
            w.currentIndexChanged[int].connect(lambda x: self.update_tool_param(param.name, x))
        else:
            w = QtWidgets.QSpinBox(parent=self)
            minimum = param.options.get("minimum", -999999999)
            maximum = param.options.get("maximum", 999999999)
            w.setMinimum(minimum)
            w.setMaximum(maximum)
            if param.default is not None:
                w.setValue(param.default)
            param.value = w.value()
            w.valueChanged[int].connect(lambda x: self.update_tool_param(param.name, x))
        return w

    def _convert_bool(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QCheckBox()
        if param.default is not None:
            w.setChecked(param.default)
        param.value = w.isChecked()
        w.stateChanged.connect(lambda x: self.update_tool_param(param.name, x == QtCore.Qt.Checked))
        return w

    def _convert_str(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            w = QtWidgets.QComboBox()
            w.addItems(param.choices)
            if param.default is not None and param.default in param.choices:
                index = w.findText(param.default)
                w.setCurrentIndex(index)
            param.value = w.currentText()
            w.currentIndexChanged[str].connect(lambda x: self.update_tool_param(param.name, x))
        else:
            w = QtWidgets.QLineEdit()
            param.value = w.text()
            w.textChanged.connect(lambda x: self.update_tool_param(param.name, x))
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
        return w

    def update_tool_param(self, name: str, value: Any):
        param: xappt.Parameter = getattr(self.tool, name)
        param.value = param.validate(value)
