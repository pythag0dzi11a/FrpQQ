class Message:
    def __init__(self, *args):
        self._message: list = []
        self._add_parts(args)

    def _add_parts(self, items):
        for item in items:
            self._message.append(item.to_dict())

    def to_list(self) -> list:
        return self._message
