#!/usr/bin/env python3
import xappt


if __name__ == '__main__':
    interface = xappt.get_interface()
    interface.invoke(xappt.get_tool_plugin("interactive1")())
