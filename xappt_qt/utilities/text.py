import markdown


def to_markdown(text: str):
    if len(text) == 0:
        return text

    md = markdown.markdown(text)
    style = "".join((
        "code {background-color: #000; color: #ccc;}",
        "ul {margin-left: -20px;}",
        "a {text-decoration: none;}",
    ))
    wrap = f"<html><head><style>{style}</style></head><body>{md}</body></html>"
    return wrap
