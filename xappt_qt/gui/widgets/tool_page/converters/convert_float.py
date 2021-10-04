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
        w.setStepType(QtWidgets.QDoubleSpinBox.AdaptiveDecimalStepType)
        for v in (param.value, param.default):
            if v is not None:
                w.setValue(v)
                break
        else:
            param.value = w.value()

        self._getter_fn = w.value
        self._setter_fn = w.setValue

        w.valueChanged[float].connect(lambda x: self.onValueChanged.emit(param.name, x))

        return w
