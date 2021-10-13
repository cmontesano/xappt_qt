from __future__ import annotations

import argparse
import os
import sys

import xappt
from xappt.config import log as logger

from xappt_qt.constants import *


def parse_unknowns_args(args: list[str], default_bool=True):
    kwarg_dict = {}
    previous_key: str = ""
    while len(args):
        this_item = args.pop(0)
        if this_item.startswith("--"):
            if previous_key:
                # we don't have a value for the last key, make it a bool
                kwarg_dict[previous_key] = default_bool
            previous_key = this_item[2:]
        else:
            if previous_key:
                kwarg_dict[previous_key] = this_item
                previous_key = ""
            else:
                logger.warning(f"Unhandled argument '{this_item}'")
    if previous_key:  # dangling key, make it a bool
        kwarg_dict[previous_key] = default_bool
    return kwarg_dict


def launch(tool_name: str, unknown_args: list[str]):
    tool_class = xappt.get_tool_plugin(tool_name)
    if tool_class is None:
        raise SystemExit(f"Tool {tool_name} not found.")

    interface = xappt.get_interface()
    interface.tool_data = parse_unknowns_args(unknown_args)
    interface.add_tool(tool_class)

    return interface.run()


def main(argv) -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME

    parser = argparse.ArgumentParser()
    parser.add_argument('toolname', help='Specify the name of the tool to load')

    options, unknowns = parser.parse_known_args(args=argv)

    return launch(options.toolname, unknowns)


def entry_point() -> int:
    return main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
