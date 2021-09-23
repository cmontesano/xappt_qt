import importlib.resources
import pathlib

from typing import Type, Union

from xappt import BaseTool
from xappt_qt.utilities.text import to_markdown

ICONS_MODULE = "xappt_qt.resources.icons"
TOOL_ICON = "tool.svg"


def get_tool_icon(tool: Union[Type[BaseTool], BaseTool]) -> pathlib.Path:
    if hasattr(tool, "custom_icon") and isinstance(tool.custom_icon, str):
        if tool.custom_icon.count("::"):
            module_path, file_name = tool.custom_icon.split("::", maxsplit=1)
        else:
            module_path = ".".join(tool.__module__.split(".")[:-1])  # get module's parent
            file_name = tool.custom_icon
        try:
            with importlib.resources.path(module_path, file_name) as path:
                icon_path = path
        except FileNotFoundError:
            pass
        else:
            return icon_path

    with importlib.resources.path(ICONS_MODULE, TOOL_ICON) as path:
        return path


def is_headless(tool: Union[Type[BaseTool], BaseTool]) -> bool:
    return getattr(tool, "headless", False)  # default: False


def help_text(tool: Union[Type[BaseTool], BaseTool], *, process_markdown: bool = True) -> str:
    if process_markdown:
        return to_markdown(tool.help())
    else:
        return tool.help()


def can_auto_advance(tool: Union[Type[BaseTool], BaseTool]) -> bool:
    return getattr(tool, "auto_advance", False)
