import argparse
import os
import sys

import xappt

from xappt_qt.constants import *


def main(argv) -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME

    parser = argparse.ArgumentParser()
    parser.add_argument('toolname', help='Specify the name of the tool to load')

    options, unknowns = parser.parse_known_args(args=argv)

    xappt.discover_plugins()

    tool_class = xappt.get_tool_plugin(options.toolname)
    if tool_class is None:
        raise SystemExit(f"Tool {options.toolname} not found.")

    interface = xappt.get_interface()
    interface.add_tool(tool_class)

    return interface.run()


def entry_point() -> int:
    return main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
