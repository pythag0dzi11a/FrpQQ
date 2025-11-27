class Message:
    def __init__(self, *args):
        self._message: list = []
        self._add_parts(args)

    def _add_parts(self, items):
        for item in items:
            self._message.append(item.to_dict())

    def to_list(self) -> list:
        return self._message


class Text:
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> dict:
        return {"type": "text", "data": {"text": self.text}}

    def to_string(self) -> str:
        return self.text


class Image:
    def __init__(
            self,
            url: str,
            name: str = "",
            summary: str = "",
            file: bytes = b"",
            sub_type: str = "",
            file_id: str = "",
    ):
        self._url = url
        self._name = name
        self._summary = summary
        self._file = file
        self._sub_type = sub_type
        self._file_id = file_id

    def to_dict(self) -> dict:
        return {
            "type": "image",
            "data": {
                "url": self._url,
                "name": self._name,
                "summary": self._summary,
                "file": self._file,
                "sub_type": self._sub_type,
                "file_id": self._file_id,
            },
        }

    def to_string(self) -> str:
        return f"![image]({self._url})"
