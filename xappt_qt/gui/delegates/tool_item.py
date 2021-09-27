from math import ceil

from PyQt5 import QtCore, QtGui, QtWidgets

from xappt_qt.gui.delegates.simple_item import SimpleItemDelegate


class ToolItemDelegate(SimpleItemDelegate):
    ROLE_TOOL_CLASS = QtCore.Qt.UserRole + 1
    ROLE_ITEM_TYPE = QtCore.Qt.UserRole + 2
    ROLE_ITEM_LIST = QtCore.Qt.UserRole + 3
    ROLE_ITEM_SEARCH_TEXT = QtCore.Qt.UserRole + 4
    ROLE_ICON_SIZE = QtCore.Qt.UserRole + 5

    ITEM_TYPE_COLLECTION = 0
    ITEM_TYPE_TOOL = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_bg_color = QtGui.QPalette().color(QtGui.QPalette.Highlight).darker(500)
        self.light_bg_color = QtGui.QPalette().color(QtGui.QPalette.Highlight)
        self.fg_color = QtGui.QPalette().color(QtGui.QPalette.ButtonText)
        self.outline_color = QtGui.QColor(0, 0, 0)
        self._hint_height = None

    def draw_arrow(self, expanded: bool, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem):
        painter.save()

        painter.setRenderHints(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHints(QtGui.QPainter.TextAntialiasing, True)
        painter.setRenderHints(QtGui.QPainter.HighQualityAntialiasing, True)

        y_scale = -1.0 if expanded else 1.0

        radius = option.rect.height() * 0.15
        arrow = QtGui.QPainterPath()
        arrow.moveTo(0.0 * radius, 1.0 * radius * y_scale)
        arrow.lineTo(0.866 * radius, -0.5 * radius * y_scale)
        arrow.lineTo(-0.866 * radius, -0.5 * radius * y_scale)
        arrow.lineTo(0.0 * radius, 1.0 * radius * y_scale)

        offset = option.rect.height() * 0.5
        arrow.translate(option.rect.right() - offset, option.rect.top() + offset)

        painter.setOpacity(0.5)
        for y in (-1, 0, 1):
            for x in (-1, 0, 1):
                painter.fillPath(arrow.translated(x, y), self.outline_color)

        painter.setOpacity(1.0)
        painter.fillPath(arrow, self.fg_color)
        painter.restore()

    def draw_bg(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem):
        painter.save()

        if option.state & QtWidgets.QStyle.State_Selected == QtWidgets.QStyle.State_Selected:
            bg_color = self.light_bg_color
        else:
            bg_color = self.dark_bg_color

        painter.fillRect(option.rect, bg_color)
        painter.setPen(self.outline_color)
        painter.drawRect(option.rect.adjusted(0, 0, -1, -1))
        painter.restore()

    def draw_caption(self, caption: str, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem):
        painter.save()

        painter.setRenderHints(QtGui.QPainter.Antialiasing, False)
        painter.setRenderHints(QtGui.QPainter.TextAntialiasing, False)
        painter.setRenderHints(QtGui.QPainter.HighQualityAntialiasing, False)

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        painter.setPen(self.outline_color)
        painter.setOpacity(0.6)
        for y in (-1, 0, 1):
            for x in (-1, 0, 1):
                painter.drawText(option.rect.translated(x, y), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, caption)

        painter.setPen(self.fg_color)
        painter.setOpacity(1.0)
        painter.drawText(option.rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, caption)
        painter.restore()

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        item_type = index.data(self.ROLE_ITEM_TYPE)

        if item_type == self.ITEM_TYPE_COLLECTION:
            painter.save()

            self.draw_bg(painter, option)

            if isinstance(option.widget, QtWidgets.QTreeView):
                self.draw_arrow(option.widget.isExpanded(index), painter, option)

            caption = f"  {index.data(QtCore.Qt.DisplayRole)}"
            self.draw_caption(caption, painter, option)
            painter.restore()
        else:
            super(ToolItemDelegate, self).paint(painter, option, index)

    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
        hint = super().sizeHint(option, index)
        # if self._hint_height is None:
        icon_size = index.data(self.ROLE_ICON_SIZE)
        if icon_size is not None:
            hint.setHeight(icon_size.height() + 12)
        return hint
