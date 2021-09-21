import time

import xappt


@xappt.register_plugin
class AutoAdvance(xappt.BaseTool):
    message = xappt.ParamString(options={"ui": "label"})
    next_iteration_advance_mode = xappt.ParamInt(choices=("no auto advance", "auto advance"))

    def __init__(self, *, interface: xappt.BaseInterface, **kwargs):
        super(AutoAdvance, self).__init__(interface=interface, **kwargs)

        self.max_iterations = 5
        self.auto_advance = bool(self.interface.tool_data.get('next_iteration_advance_mode', 0))

        self.iteration = self.interface.tool_data.get("iteration", 1)
        if self.iteration == self.max_iterations:
            step = "last"
            self.next_iteration_advance_mode.hidden = True
        else:
            step = xappt.humanize_ordinal(self.iteration)

        self.message.value = f"This is the {step} of {self.max_iterations} iterations of this tool."

    @classmethod
    def name(cls) -> str:
        return 'auto-advance'

    @classmethod
    def help(cls) -> str:
        return ("When using a tool in the Qt interface, the default behavior is to leave the tool disabled "
                "after a successful execution. Clicking **Next** or **Close** will move to the next tool or "
                "close the interface.\n\nYou can set an attribute named `auto_advance`, and when it's set "
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

        last_iteration = self.iteration == self.max_iterations
        if last_iteration:
            if self.auto_advance:
                self.interface.message("Auto Advance is enabled for this iteration.\n\nOnce you click OK "
                                       "on this message the interface will automatically exit.")
            else:
                self.interface.message("Auto Advance is disabled for this iteration.\n\nOnce you click OK "
                                       "on this message, click the Close button to exit this interface.")
        else:
            self.interface.add_tool(AutoAdvance)
            if self.auto_advance:
                self.interface.message("Auto Advance is enabled for this iteration.\n\nOnce you click OK "
                                       "on this message the next iteration will be automatically loaded.")
            else:
                self.interface.message("Auto Advance is disabled for this iteration.\n\nOnce you click OK "
                                       "on this message click the Next button to continue to the next "
                                       "iteration.")

        self.interface.tool_data['iteration'] = self.iteration + 1
        self.interface.tool_data['next_iteration_advance_mode'] = self.next_iteration_advance_mode.value

        return 0
