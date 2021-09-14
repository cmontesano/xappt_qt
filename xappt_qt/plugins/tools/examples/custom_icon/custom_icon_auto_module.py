import xappt


@xappt.register_plugin
class CustomIconAutoModule(xappt.BaseTool):
    custom_icon = "icon2.svg"

    @classmethod
    def name(cls) -> str:
        return "custom-icon-auto-module"

    @classmethod
    def help(cls) -> str:
        return ("This tool will display a custom icon in the xappt_qt browser and the Qt interface's "
                "dialog. Note that the tool dialog will only display the custom icon of the first "
                "loaded tool. This plugin sets a class variable named `custom_icon` with a string "
                "value representing a file name that will be loaded using importlib.resources. The "
                "module will be automatically derived by examining this tool's class.")

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.message("Complete")
        return 0
