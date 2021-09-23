import xappt


@xappt.register_plugin
class StringUi(xappt.BaseTool):
    plain_string = xappt.ParamString()

    choice_string = xappt.ParamString(choices=("apple", "banana", "cantaloupe"))

    folder_select = xappt.ParamString(
        options={'ui': 'folder-select'},
        validators=[xappt.ValidateFolderExists])

    file_open = xappt.ParamString(
        options={'ui': 'file-open', "accept": ('Text Files *.txt', 'Images *.png;*.jpg;')},
        validators=[xappt.ValidateFileExists])

    file_save = xappt.ParamString(
        options={'ui': 'file-save', "accept": ('Text Files *.txt', 'All Files *.*')})

    multi_line = xappt.ParamString(options={'ui': 'multi-line'})

    label = xappt.ParamString(
        options={'ui': 'label'},
        value='Labels support <a href="https://www.w3.org/html/">HTML</a> with clickable links')

    markdown = xappt.ParamString(
        options={'ui': 'markdown'},
        value='Strings _also_ support [Markdown](https://daringfireball.net/projects/markdown/).\n\n'
              'Captions are **automatically** hidden when using the `label` or `markdown` ui.')

    password = xappt.ParamString(options={'ui': 'password'})

    csv_string = xappt.ParamString(
        options={
            'ui': 'csv',
            'header_row': True,
            'editable': True,
            'csv_import': True,
            'csv_export': True,
            'sorting_enabled': True
        },
        value=(
            'header1,header2,header3\n'
            'value1,value6,123\n'
            'value2,value5,12\n'
            'value3,value4,1234\n'
            'value4,value3,234\n'
            'value5,value2,3456\n'
            'value6,value1,12345\n'
        ))

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
            "* password\n"
            "* csv\n"
        )

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        return 0
