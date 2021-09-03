from PyQt5 import QtCore, QtWidgets

import xappt

from xappt_qt.gui.widgets.tool_page.converters.base import ParameterWidgetBase


class ParameterWidgetBool(ParameterWidgetBase):
    def get_widget(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        if param.options.get("ui") == "button":
            w = QtWidgets.QPushButton(parent=self)
            w.setText(self.get_caption(param))
            w.clicked.connect(lambda x: self.update_tool_param(param.name, param.value))
            self.caption = ""

            self._getter_fn = lambda: True
            self._setter_fn = lambda x: True
        else:
            w = QtWidgets.QCheckBox(parent=self)
            for v in (param.value, param.default):
                if v is not None:
                    w.setChecked(v)
                    break
            else:
                param.value = w.isChecked()
            w.stateChanged.connect(lambda x: self.onValueChanged.emit(param.name, x == QtCore.Qt.Checked))

            self._getter_fn = w.isChecked
            self._setter_fn = w.setChecked

        return w
