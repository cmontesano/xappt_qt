import sys

from PyQt5 import QtCore

import xappt
import xappt_qt

from xappt_qt.gui.ui.browser_tab_about import Ui_tabAbout
from xappt_qt.gui.tab_pages.base import BaseTabPage

app_info = {
    "xappt_qt": {
        "version": xappt_qt.version_str,
        "url": "https://github.com/cmontesano/xappt_qt.git",
    },
    "xappt": {
        "version": xappt.version_str,
        "url": "https://github.com/cmontesano/xappt.git",
    },
    "python": {
        "version": ".".join(map(str, sys.version_info[:3])),
        "url": "https://www.python.org",
    },
    "PyQt": {
        "version": QtCore.PYQT_VERSION_STR,
        "url": "https://riverbankcomputing.com/software/pyqt/",
    },
}


class AboutTabPage(BaseTabPage, Ui_tabAbout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setupUi(self)
        self.txtAbout.setHtml(self.generate_html())

    @staticmethod
    def generate_html() -> str:
        html = ['<table cellspacing="4" cellpadding="4">']

        for name, app_data in app_info.items():
            url = app_data['url']
            version = app_data['version']
            html.append(f'<tr><td><a href="{url}" style="text-decoration: none;">{name}</a></td><td>{version}</td></tr>')

        html.append("</table>")

        return "\n".join(html)
