import time

import xappt


class AutoAdvanceBase(xappt.BaseTool):
    message = xappt.ParamString(options={"ui": "label"})

    def __init__(self, *, interface: xappt.BaseInterface, **kwargs):
        super(AutoAdvanceBase, self).__init__(interface=interface, **kwargs)
        self.message.value = self.message_label_text()

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def help(cls) -> str:
        return ("When using a tool in the Qt interface, the default behavior is to leave the tool disabled "
                "after a successful execution. Clicking **Next** or **Close** will move to the next tool or "
                "close the interface.\n\nYou can set a class attribute named `auto_advance`, and when it's set "
                "to `True` the next tool will be automatically loaded (or the interface wil be closed) after "
                "a successful execution.")

    def message_label_text(self) -> str:
        raise NotImplementedError

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.progress_start()
        for i in range(100):
            progress = (i + 1) / 100.0
            self.interface.progress_update(f"Iteration: {i + 1}/100", progress)
            time.sleep(0.01)
        self.interface.progress_end()
        return 0


@xappt.register_plugin
class AutoAdvanceStart(AutoAdvanceBase):
    @classmethod
    def name(cls) -> str:
        return 'auto-advance'

    def message_label_text(self) -> str:
        return "This tool will not auto advance."

    def execute(self, **kwargs) -> int:
        super().execute(**kwargs)
        self.interface.message("Execution is complete. After clicking 'OK' you will have to "
                               "click the 'Next' button to load the next tool.")
        self.interface.add_tool(AutoAdvanceAuto)
        return 0


class AutoAdvanceAuto(AutoAdvanceBase):
    auto_advance = True

    @classmethod
    def name(cls) -> str:
        return 'auto-advance-auto'

    def message_label_text(self) -> str:
        return "This tool will automatically advance to the next tool."

    def execute(self, **kwargs) -> int:
        super().execute(**kwargs)
        self.interface.message("Execution is complete. After clicking 'OK' the next tool "
                               "will be automatically loaded.")
        self.interface.add_tool(AutoAdvanceClose)
        return 0


class AutoAdvanceClose(AutoAdvanceBase):
    auto_advance = True

    @classmethod
    def name(cls) -> str:
        return 'auto-advance-close'

    def message_label_text(self) -> str:
        return "This tool will automatically close the interface."

    def execute(self, **kwargs) -> int:
        super().execute(**kwargs)
        self.interface.message("Execution is complete. After clicking 'OK' the interface "
                               "will automatically close.")
        return 0
