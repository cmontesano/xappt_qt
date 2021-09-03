from PyQt5 import QtCore, QtWidgets


class TextEdit(QtWidgets.QPlainTextEdit):
    editingFinished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._changed = False
        self.setTabChangesFocus(True)
        self.textChanged.connect(self._handle_text_changed)
        self.setLineWrapMode(self.NoWrap)

    def focusOutEvent(self, event):
        if self._changed:
            self.editingFinished.emit()
        super().focusOutEvent(event)

    def _handle_text_changed(self):
        self._changed = True

    def setTextChanged(self, state=True):
        self._changed = state

    def setText(self, text: str):
        self.setPlainText(text)
        self._changed = False

    def text(self) -> str:
        return self.toPlainText()
