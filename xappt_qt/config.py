console_word_wrap = False
console_auto_scroll = True

# https://doc.qt.io/qt-5/stylesheet-reference.html#paletterole
console_color_stdout = "palette(window-text)"
console_color_stderr = "#f55"


def load_settings():
    import json
    from xappt_qt.constants import APP_CONFIG_PATH
    config_path = APP_CONFIG_PATH.joinpath("settings.cfg")
    try:
        with open(config_path, "r") as fp:
            settings_raw = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    else:
        global console_word_wrap
        console_word_wrap = settings_raw.get('console_word_wrap', False)
        global console_auto_scroll
        console_auto_scroll = settings_raw.get('console_auto_scroll', True)


load_settings()
del load_settings
