import xappt


@xappt.register_plugin
class ParamVisibility(xappt.BaseTool):
    param1 = xappt.ParamString(hidden=True)
    param2 = xappt.ParamString()

    toggle_param1 = xappt.ParamBool()
    toggle_param2 = xappt.ParamBool()

    @classmethod
    def name(cls) -> str:
        return "param-visibility"

    @classmethod
    def help(cls) -> str:
        return ""

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def __init__(self, *, interface: xappt.BaseInterface, **kwargs):
        super().__init__(interface=interface, **kwargs)
        self.toggle_param1.on_value_changed.add(self.on_param_value_changed)
        self.toggle_param2.on_value_changed.add(self.on_param_value_changed)

    def on_param_value_changed(self, param: xappt.Parameter):
        if param == self.toggle_param1:
            self.param1.hidden = not self.param1.hidden
        if param == self.toggle_param2:
            self.param2.hidden = not self.param2.hidden

    def execute(self, **kwargs) -> int:
        return 0
