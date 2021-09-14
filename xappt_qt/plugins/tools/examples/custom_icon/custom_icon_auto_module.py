import xappt


@xappt.register_plugin
class CustomIconAutoModule(xappt.BaseTool):
    custom_icon = "icon2.svg"

    @classmethod
    def name(cls) -> str:
        return "custom-icon-auto-module"

    @classmethod
    def help(cls) -> str:
        return ("This tool will display a custom icon in the **xappt_qt browser** and the **Tool dialog**.\n "
                "A class variable named `custom_icon` is set with a string value representing an image file name.\n "
                "The module containing this tool's class will automatically derived, and will be used in conjunction "
                "with the image file name to retrieve a file path using `importlib.resources`.\n\n " 
                "*Note that the tool dialog will only display the custom icon of the first loaded tool.*")

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.message("Complete")
        return 0
