import os

from . import dark_palette
from xappt_qt import constants


def apply_style(app):
    xappt_qt_stylesheet = os.getenv(constants.APP_STYLESHEET_ENV)
    if xappt_qt_stylesheet is not None and os.path.isfile(xappt_qt_stylesheet):
        with open(xappt_qt_stylesheet, 'r') as fp:
            custom_stylesheet = fp.read()
        app.setStyleSheet(custom_stylesheet)
    else:
        dark_palette.apply_palette(app)
