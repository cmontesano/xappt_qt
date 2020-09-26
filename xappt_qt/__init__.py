import os

from .interface import QtInterface

# suppress "qt.qpa.xcb: QXcbConnection: XCB error: 3 (BadWindow)"
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
