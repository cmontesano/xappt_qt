#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# adapted from https://gist.github.com/lschmierer/443b8e21ad93e2a2d7eb

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

PRIMARY_COLOR = QColor(32, 32, 32)
SECONDARY_COLOR = PRIMARY_COLOR.darker(150)
HIGHLIGHT_COLOR = QColor(128, 176, 73)
BRIGHT_COLOR = QColor(192, 192, 192)
DISABLED_COLOR = QColor(64, 64, 64)


# noinspection PyUnresolvedReferences
def apply_palette(app):
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, PRIMARY_COLOR)
    dark_palette.setColor(QPalette.WindowText, BRIGHT_COLOR)
    dark_palette.setColor(QPalette.Base, SECONDARY_COLOR)
    dark_palette.setColor(QPalette.AlternateBase, PRIMARY_COLOR)
    dark_palette.setColor(QPalette.ToolTipBase, BRIGHT_COLOR)
    dark_palette.setColor(QPalette.ToolTipText, BRIGHT_COLOR)
    dark_palette.setColor(QPalette.Text, BRIGHT_COLOR)
    dark_palette.setColor(QPalette.Button, PRIMARY_COLOR)
    dark_palette.setColor(QPalette.ButtonText, BRIGHT_COLOR)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, HIGHLIGHT_COLOR)
    dark_palette.setColor(QPalette.Highlight, HIGHLIGHT_COLOR)
    dark_palette.setColor(QPalette.HighlightedText, SECONDARY_COLOR)

    dark_palette.setColor(QPalette.Light, PRIMARY_COLOR)

    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, DISABLED_COLOR)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, DISABLED_COLOR)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, DISABLED_COLOR)

    app.setPalette(dark_palette)
    app.setStyleSheet("""
        QToolTip { 
            color: palette(text); 
            background-color: palette(window); 
            border: 1px solid palette(highlight);
            border-radius: 2px;
            padding: 2px 8px;
            min-width: 300px;
        }

        QPlainTextEdit {
            border: 1px solid palette(base);
            border-radius: 3px;
            background-color: palette(base);
            padding: 1px;
        }

        QPlainTextEdit:focus {
            border-color: palette(highlight);
        }

        QHeaderView::section {
            padding: 8px 16px;
        }
    """)
