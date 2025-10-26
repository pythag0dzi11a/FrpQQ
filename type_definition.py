class Text:
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> dict:
        return {
            "type": "text",
            "data": {
                "text": self.text
            }
        }

    def to_string(self) -> str:
        return self.text
