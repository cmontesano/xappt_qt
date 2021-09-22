import xappt


@xappt.register_plugin
class StringUi(xappt.BaseTool):
    plain_string = xappt.ParamString()

    folder_select = xappt.ParamString(
        options={'ui': 'folder-select'},
        validators=[xappt.ValidateFolderExists])

    file_open = xappt.ParamString(
        options={'ui': 'file-open', "accept": ('Text Files *.txt', 'Images *.png;*.jpg;')},
        validators=[xappt.ValidateFileExists])

    file_save = xappt.ParamString(
        options={'ui': 'file-save', "accept": ('Text Files *.txt', 'All Files *')})

    multi_line = xappt.ParamString(
        options={'ui': 'multi-line'})

    label = xappt.ParamString(
        options={'ui': 'label'},
        value='Labels support <a href="https://www.w3.org/html/">HTML</a> with clickable links')

    markdown = xappt.ParamString(
        options={'ui': 'markdown'},
        value='Strings _also_ support [Markdown](https://daringfireball.net/projects/markdown/)')

    @classmethod
    def name(cls):
        return "string-ui"

    @classmethod
    def help(cls) -> str:
        return (
            "This is an example showing the many ui options for string widgets:\n\n"
            "* folder-select\n"
            "* file-open\n"
            "* file-save\n"
            "* multi-line\n"
            "* label\n"
            "* markdown\n"
        )

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        return 0
