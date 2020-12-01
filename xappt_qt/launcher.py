import argparse
import sys

from typing import Dict, List, Type

from PyQt5 import QtWidgets

import xappt
from xappt.models.parameter import convert

from xappt_qt.gui.utilities.dark_palette import apply_palette
from xappt_qt.constants import *


def main(argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('toolname', help='Specify the name of the tool to load')

    options, unknowns = parser.parse_known_args(args=argv)

    xappt.discover_plugins()

    tool_class = xappt.get_tool_plugin(options.toolname)
    if tool_class is None:
        raise SystemExit(f"Tool {options.toolname} not found.")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(argv)
    apply_palette(app)

    app.setProperty(APP_PROPERTY_RUNNING, True)

    interface = xappt.get_interface()
    params = params_from_args(tool_class=tool_class, tool_args=unknowns)
    tool_instance = tool_class(interface=interface, **params)
    interface.invoke(tool_instance)

    return app.exec_()


def params_from_args(tool_class: Type[xappt.BaseTool], tool_args: List[str]) -> Dict:
    if not tool_args:
        return {}

    tool_parser = argparse.ArgumentParser()

    for parameter in tool_class.class_parameters():
        setup_args = parameter.param_setup_args
        args, kwargs = convert.to_argument_dict(setup_args)
        kwargs['required'] = False
        tool_parser.add_argument(*args, **kwargs)

    tool_options, _ = tool_parser.parse_known_args(args=tool_args)
    return {k: v for k, v in vars(tool_options).items() if v is not None}


def entry_point() -> int:
    return main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
