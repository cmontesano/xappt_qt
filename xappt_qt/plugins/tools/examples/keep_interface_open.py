import time

import xappt


@xappt.register_plugin
class KeepInterfaceOpen(xappt.BaseTool):
    iterations = xappt.ParamInt(options={"ui": "slider", "ticks": 1}, minimum=0, maximum=100, default=50,
                                description="Pick a number between 1 and 100, or choose 0 to close the tool.")

    @classmethod
    def name(cls) -> str:
        return "keep-ui-open"

    @classmethod
    def help(cls) -> str:
        return "An example of keeping the Qt interface open. By default it will close after a tool finishes."

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.progress_start()
        iterations = self.iterations.value
        for i in range(iterations):
            progress = (i + 1) / iterations
            self.interface.progress_update(f"Iteration: {i + 1}/{iterations}", progress)
            time.sleep(0.05)
        self.interface.progress_end()

        self.interface.message("Complete")

        if iterations > 0:
            # queue another instance of this class
            self.interface.add_tool(self.__class__)

            # make sure the next instance is initialized with the same iterations as this instance
            self.interface.tool_data['iterations'] = iterations

        return 0
