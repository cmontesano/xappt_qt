import argparse
import os
import sys

import xappt
import xappt_qt
import xappt_qt.browser
import xappt_qt.launcher

from xappt_qt.constants import APP_INTERFACE_NAME


if getattr(xappt_qt, "__compiled__", None) is not None:
    xappt_qt.executable = os.path.abspath(sys.argv[0])
elif getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    xappt_qt.executable = os.path.abspath(sys.executable)


def main() -> int:
    os.environ[xappt.INTERFACE_ENV] = APP_INTERFACE_NAME

    parser = argparse.ArgumentParser()
    parser.add_argument('toolname', type=str, help='Specify the name of the tool to load', nargs='?')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Display the version number and build')

    options, unknowns = parser.parse_known_args()

    if options.version:
        print(f"xappt_qt {xappt_qt.version_str}")

    if options.toolname is None:
        return xappt_qt.browser.main(sys.argv)
    else:
        return xappt_qt.launcher.launch(options.toolname, unknown_args=unknowns)


if __name__ == '__main__':
    sys.exit(main())
