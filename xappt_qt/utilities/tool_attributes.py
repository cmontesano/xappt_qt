import importlib.resources
import pathlib

from typing import Type

import markdown

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
    return getattr(tool_class, "headless", False)  # default: False


def help_text(tool_class: Type[BaseTool], *, process_markdown: bool = True) -> str:
    if process_markdown:
        md = markdown.markdown(tool_class.help())
        style = "".join((
            "code {background-color: #000; color: #ccc;}",
            "ul {margin-left: -20px;}",
        ))
        wrap = f"<html><head><style>{style}</style></head><body>{md}</body></html>"
        return wrap
    else:
        return tool_class.help()


def can_auto_advance(tool_class: Type[BaseTool]) -> bool:
    return getattr(tool_class, "auto_advance", False)
