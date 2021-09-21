from PyQt5 import QtWidgets

import xappt

from xappt_qt.gui.widgets.tool_page.converters.base import ParameterWidgetBase


class ParameterWidgetFloat(ParameterWidgetBase):
    def get_widget(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QDoubleSpinBox(parent=self)
        minimum = param.options.get("minimum", -999999999.0)
        maximum = param.options.get("maximum", 999999999.0)
        w.setMinimum(minimum)
        w.setMaximum(maximum)
        if param.default is not None:
            w.setValue(param.default)
        param.value = w.value()

        w.valueChanged[float].connect(lambda x: self.onValueChanged.emit(param.name, x))

        self._getter_fn = w.value
        self._setter_fn = w.setValue

        return w
