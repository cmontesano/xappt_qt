from typing import Any, Callable, Dict, Generator, Optional, Type

from PyQt5 import QtWidgets, QtCore

import xappt

from xappt_qt.gui.widgets.tool_page.converters import *
from xappt_qt.gui.widgets.error_label import ErrorLabel


class ToolPage(QtWidgets.QWidget):
    def __init__(self, tool: xappt.BaseTool, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self.convert_dispatch: Dict[Type, Callable] = {
            int: ParameterWidgetInt,
            bool: ParameterWidgetBool,
            float: ParameterWidgetFloat,
            str: ParameterWidgetStr,
            list: ParameterWidgetList,
        }

        self.vertical_expand = False

        self.tool = tool
        self.build_ui()

    # noinspection PyAttributeOutsideInit
    def build_ui(self):
        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(0, 0)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(8)

        self.setLayout(self.grid)
        self._load_tool_parameters()

    def _convert_parameter(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        widget_class = self.convert_dispatch[param.data_type]
        widget_instance: ParameterWidgetBase = widget_class(parameter=param, parent=self)
        widget_instance.onValueChanged.connect(self.on_widget_value_changed)
        return widget_instance

    def _load_tool_parameters(self):
        index = 0
        for param in self.tool.parameters():
            widget_instance = self._convert_parameter(param)
            if widget_instance.sizePolicy().verticalPolicy() == QtWidgets.QSizePolicy.Expanding:
                self.vertical_expand = True

            if len(widget_instance.caption):
                label = QtWidgets.QLabel(widget_instance.caption)
                label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                label.setToolTip(param.description)
                param.metadata['label'] = label
                self.grid.addWidget(label, index, 0)

            error = ErrorLabel()
            param.metadata['error'] = error
            self.grid.addWidget(error, index, 2)

            widget_instance.setToolTip(param.description)
            param.metadata['widget'] = widget_instance  # this lets us avoid lambdas
            self.grid.addWidget(widget_instance, index, 1)

            self.parameter_options_updated(param)
            self.parameter_visibility_updated(param)

            param.on_choices_changed.add(self.update_tool_choices)
            param.on_value_changed.add(self.parameter_value_updated)
            param.on_options_changed.add(self.parameter_options_updated)
            param.on_visibility_changed.add(self.parameter_visibility_updated)

            index += 1

    def ordered_widgets(self) -> Generator[QtWidgets.QWidget, None, None]:
        for row in range(self.grid.rowCount()):
            layout_item = self.grid.itemAtPosition(row, 1)
            if layout_item is None:
                continue
            widget = layout_item.widget()
            if widget is not None:
                yield widget

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

        # create a new widget to replace it
        new_widget = self._convert_parameter(param)

        new_widget.setToolTip(param.description)
        param.metadata['widget'] = new_widget
        self.grid.addWidget(new_widget, row, column)
        self.parameter_options_updated(param)

    def on_widget_value_changed(self, param_name: str, param_value: Any):
        parameter: xappt.Parameter = getattr(self.tool, param_name)
        error_widget: ErrorLabel = parameter.metadata["error"]

        try:
            parameter.value = parameter.validate(param_value)
        except xappt.ParameterValidationError as err:
            error_widget.set_error(str(err))
        else:
            error_widget.reset()

    @staticmethod
    def parameter_value_updated(param: xappt.Parameter):
        """ Update widget with the parameter's new value """
        widget = param.metadata.get('widget')
        assert widget is not None
        setter = param.metadata.get('ui-setter')
        assert setter is not None

        # Block signals to avoid infinite recursion:
        #    Updating the widget's value here can trigger the widget's onValueChanged
        #    signal, which would then update the parameter, cause its on_value_changed
        #    callback to be invoked, and then then trigger this function leading which
        #    would start the process over again.
        widget.blockSignals(True)
        setter(param.value)
        widget.blockSignals(False)

    @staticmethod
    def parameter_options_updated(param: xappt.Parameter):
        widget: Optional[QtWidgets.QWidget] = param.metadata.get('widget')

        enabled = param.option("enabled", True)
        if widget is not None:
            widget.setEnabled(enabled)

    @staticmethod
    def parameter_visibility_updated(param: xappt.Parameter):
        label: Optional[QtWidgets.QLabel] = param.metadata.get('label')
        widget: Optional[QtWidgets.QWidget] = param.metadata.get('widget')
        error: Optional[ErrorLabel] = param.metadata.get('error')

        if label is not None:
            label.setVisible(not param.hidden)
        if widget is not None:
            widget.setVisible(not param.hidden)
        if error is not None:
            error.setVisible(not param.hidden)

    def disconnect(self):
        for param in self.tool.parameters():
            param.on_value_changed.clear()
            param.on_options_changed.clear()
            param.on_choices_changed.clear()
