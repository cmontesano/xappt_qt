import argparse
import sys

from PyQt5 import QtWidgets
import xappt

from xappt_qt.gui.utilities.dark_palette import apply_palette
from xappt_qt.constants import *


def main(argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('toolname', help='Specify the name of the tool to load')

    options = parser.parse_args(args=argv)

    xappt.discover_plugins()

    tool_class = xappt.get_tool_plugin(options.toolname)
    if tool_class is None:
        raise SystemExit(f"Tool {options.toolname} not found.")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(argv)
    apply_palette(app)

    app.setProperty(APP_PROPERTY_RUNNING, True)

    interface = xappt.get_interface()
    tool_instance = tool_class(interface=interface)
    interface.invoke(tool_instance)

    return app.exec_()


def entry_point() -> int:
    return main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
