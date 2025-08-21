class Text:
    def __init__(self, text: str, style: str | None = None):
        self.plain = text
        self.text = text
        self.style = style
    def __str__(self) -> str:
        return self.text
