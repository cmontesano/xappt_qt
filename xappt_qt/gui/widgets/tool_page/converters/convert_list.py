from __future__ import annotations

from PyQt5 import QtWidgets

import xappt

from xappt_qt.gui.widgets.tool_page.converters.base import ParameterWidgetBase
from xappt_qt.gui.widgets.check_list import CheckList


class ParameterWidgetList(ParameterWidgetBase):
    def get_widget(self, param: xappt.Parameter) -> QtWidgets.QWidget:
        w = CheckList(searchable=param.options.get('searchable', False))
        if param.choices is not None:
            w.add_items(param.choices)
        for v in (param.value, param.default):
            if v is not None:
                w.check_items(v)
                break
        param.value = list(w.checked_items())
        w.item_changed.connect(lambda: self.onValueChanged.emit(param.name, self.value))

        self._getter_fn = lambda widget=w: list(widget.checked_items())
        self._setter_fn = lambda value, widget=w: self.set_list_value(value, widget)

        return w

    @staticmethod
    def set_list_value(items: list[str], widget: CheckList):
        widget.uncheck_all()
        widget.check_items(items)
