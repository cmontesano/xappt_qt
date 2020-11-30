import argparse
import sys

from typing import Dict, List, Type

from PyQt5 import QtWidgets

import xappt
from xappt.cli import add_tool_args

from xappt_qt.gui.utilities.dark_palette import apply_palette
from xappt_qt.constants import *


def main(argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('toolname', help='Specify the name of the tool to load')
    parser.add_argument('param_defaults', nargs=argparse.REMAINDER)

    options, unknowns = parser.parse_known_args(args=argv)

    xappt.discover_plugins()

    tool_class = xappt.get_tool_plugin(options.toolname)
    if tool_class is None:
        raise SystemExit(f"Tool {options.toolname} not found.")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(argv)
    apply_palette(app)

    app.setProperty(APP_PROPERTY_RUNNING, True)

    interface = xappt.get_interface()
    params = params_from_args(tool_class=tool_class, args=unknowns)
    tool_instance = tool_class(interface=interface, **params)
    interface.invoke(tool_instance)

    return app.exec_()


def params_from_args(tool_class: Type[xappt.BaseTool], args: List) -> Dict:
    if not len(args):
        return {}

    tool_parser = argparse.ArgumentParser()
    add_tool_args(parser=tool_parser, plugin_class=tool_class)
    for action in tool_parser._actions:  # type: argparse.Action
        action.required = False

    tool_options, _ = tool_parser.parse_known_args(args=args)
    params = vars(tool_options)
    for key, value in list(params.items()):
        if value is None:
            params.pop(key)
    return params


def entry_point() -> int:
    return main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
