import sys

from PySide2 import QtWidgets

import xappt

from xappt_qt.dark_palette import apply_palette


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    apply_palette(app)

    xappt.interface.invoke(xappt.get_tool_plugin("interactive2")())
