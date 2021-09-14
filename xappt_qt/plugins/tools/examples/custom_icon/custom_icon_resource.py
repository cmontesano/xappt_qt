import xappt


@xappt.register_plugin
class CustomIconResource(xappt.BaseTool):
    custom_icon = "xappt_qt.plugins.tools.examples.custom_icon::icon1.svg"

    @classmethod
    def name(cls) -> str:
        return "custom-icon-resource"

    @classmethod
    def help(cls) -> str:
        return ("This tool will display a custom icon in the xappt_qt browser and the Qt interface's "
                "dialog. Note that the tool dialog will only display the custom icon of the first "
                "loaded tool. This plugin sets a class variable named `custom_icon` with a string "
                "value representing a module and a file name that will be used by importlib.resources "
                "to load an image file. This string is encoded with '::' separating the module and "
                "file name (e.g. 'module.name::file.ext')")

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.message("Complete")
        return 0
