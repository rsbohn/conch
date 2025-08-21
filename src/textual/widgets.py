from types import SimpleNamespace

class Input:
    def __init__(self, placeholder: str = "", id: str | None = None):
        self.placeholder = placeholder
        self.id = id
        self.value = ""
        self.border_title = ""
        self.styles = SimpleNamespace(border=None)

class Static:
    def __init__(self, text: str = "", id: str | None = None):
        self.text = text
        self.id = id
    def update(self, msg: str):
        self.text = msg

class Footer:
    pass

class RichLog:
    def __init__(self, *args, **kwargs):
        self._lines = []
        self.border_title = ""
        self.can_focus = False
        self.auto_scroll = False
        self.size = SimpleNamespace(height=0)
    def write(self, text):
        self._lines.append(text)
    def clear(self):
        self._lines.clear()
    @property
    def lines(self):
        return self._lines
    @lines.setter
    def lines(self, value):
        self._lines = list(value)
    def scroll_to(self, y=0):
        pass
