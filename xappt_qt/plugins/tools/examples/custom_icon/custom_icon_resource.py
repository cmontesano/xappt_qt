import xappt


@xappt.register_plugin
class CustomIconResource(xappt.BaseTool):
    custom_icon = "xappt_qt.plugins.tools.examples.custom_icon::icon1.svg"

    @classmethod
    def name(cls) -> str:
        return "custom-icon-resource"

    @classmethod
    def help(cls) -> str:
        return ("This tool will display a custom icon in the **xappt_qt browser** and the **Tool dialog**.\n "
                "A class variable named `custom_icon` is set with a string value representing a module path "
                "and a file name bundled with that module.\n This information will be used with "
                "`importlib.resources` to retrieve the image's file path.\n\n"
                "*Note that the tool dialog will only display the custom icon of the first loaded tool.*")

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.message("Complete")
        return 0
