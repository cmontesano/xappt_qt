import os
import sys

import xappt_qt
import xappt_qt.browser
import xappt_qt.launcher


def main() -> int:
    if len(sys.argv) == 1:
        return xappt_qt.browser.entry_point()
    else:
        return xappt_qt.launcher.entry_point()


if __name__ == '__main__':
    if getattr(xappt_qt, "__compiled__", None) is not None:
        xappt_qt.executable = os.path.abspath(sys.argv[0])
    sys.exit(main())
