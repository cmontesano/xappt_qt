import importlib.resources
import pathlib

from typing import Type

from xappt import BaseTool

ICONS_MODULE = "xappt_qt.resources.icons"
TOOL_ICON = "tool.svg"


def get_tool_icon(tool_class: Type[BaseTool]) -> pathlib.Path:
    if hasattr(tool_class, "custom_icon") and isinstance(tool_class.custom_icon, str):
        if tool_class.custom_icon.count("::"):
            module_path, file_name = tool_class.custom_icon.split("::", maxsplit=1)
        else:
            module_path = ".".join(tool_class.__module__.split(".")[:-1])  # get module's parent
            file_name = tool_class.custom_icon
        try:
            with importlib.resources.path(module_path, file_name) as path:
                icon_path = path
        except FileNotFoundError:
            pass
        else:
            return icon_path

    with importlib.resources.path(ICONS_MODULE, TOOL_ICON) as path:
        return path


def is_headless(tool_class: Type[BaseTool]) -> bool:
    return hasattr(tool_class, "headless") and tool_class.headless
