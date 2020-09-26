import os
import sys

from PySide2 import QtWidgets

import xappt

from xappt_qt.dark_palette import apply_palette


if __name__ == '__main__':
    # suppress "qt.qpa.xcb: QXcbConnection: XCB error: 3 (BadWindow)"
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

    app = QtWidgets.QApplication(sys.argv)
    apply_palette(app)

    xappt.interface.invoke(xappt.get_tool_plugin("interactive1")())

    sys.exit(app.exec_())
