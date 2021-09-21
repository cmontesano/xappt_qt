from PyQt5 import QtWidgets, QtCore

import xappt

from xappt_qt.gui.widgets.tool_page.converters.base import ParameterWidgetBase


class ParameterWidgetInt(ParameterWidgetBase):
    def get_widget(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.choices is not None:
            return self._convert_int_choice(param)
        else:
            return self._convert_int(param)

    def _convert_int_choice(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = QtWidgets.QComboBox(parent=self)
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

        self._setup_combobox(param, w)

        w.currentIndexChanged[str].connect(lambda x: self.onValueChanged.emit(param.name, x))

        self._getter_fn = w.currentIndex
        self._setter_fn = w.setCurrentIndex

        return w

    def _convert_int(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        minimum = param.options.get("minimum")
        maximum = param.options.get("maximum")

        ui = param.options.get("ui")
        if ui == "slider" and minimum is not None and maximum is not None:
            w = QtWidgets.QSlider(parent=self)
            w.setOrientation(QtCore.Qt.Horizontal)
            ticks = param.options.get("ticks", 0)
            if ticks == 0:
                w.setTickPosition(QtWidgets.QSlider.NoTicks)
            else:
                w.setTickPosition(QtWidgets.QSlider.TicksBelow)
                w.setTickInterval(ticks)
        else:
            w = QtWidgets.QSpinBox(parent=self)
            if minimum is None:
                minimum = -999999999
            if maximum is None:
                maximum = 999999999
        w.setMinimum(minimum)
        w.setMaximum(maximum)
        for v in (param.value, param.default):
            if v is not None:
                w.setValue(v)
                break
        else:
            param.value = w.value()
        w.valueChanged[int].connect(lambda x: self.onValueChanged.emit(param.name, x))

        self._getter_fn = w.value
        self._setter_fn = w.setValue

        return w
