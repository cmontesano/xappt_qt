from PyQt5 import QtWidgets, QtGui, QtCore

from xappt_qt.gui.application import get_application


def center_widget(widget: QtWidgets.QWidget):
    app = get_application()
    cursor_pos = QtGui.QCursor.pos()
    screen = app.screenAt(cursor_pos)
    screen_rect = screen.availableGeometry()
    window_rect = QtCore.QRect(QtCore.QPoint(0, 0), widget.frameSize().boundedTo(screen_rect.size()))
    widget.resize(window_rect.size())
    widget.move(screen_rect.center() - window_rect.center())
