import time

import xappt


@xappt.register_plugin
class HeadlessExecution(xappt.BaseTool):
    headless = True

    @classmethod
    def name(cls) -> str:
        return "headless"

    @classmethod
    def help(cls) -> str:
        return ("A headless tool will run with no interface, except for a progress bar and "
                "message dialogs. \nTo make a tool headless, simply add a class variable "
                "named `headless`, and set its value to **True**.")

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, *, interface: xappt.BaseInterface, **kwargs) -> int:
        interface.progress_start()
        for i in range(10):
            interface.progress_update(f"Working...", (i + 1) / 10)
            time.sleep(0.5)
        interface.progress_end()

        interface.message("Complete")

        return 0
