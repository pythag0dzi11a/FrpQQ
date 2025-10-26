import json


class Config:
    __slots__ = (
        "user_name",
        "password",
        "napcat_server_addr",
        "http_server_port",
        "ws_server_port",
    )

    def __init__(self):
        with open('config.json', 'r') as f:
            __config = json.load(f)

            self.user_name = __config.get("user_name")
            self.password = __config.get("password")

            self.napcat_server_addr = __config.get("napcat_server_addr")
            self.http_server_port = __config.get("http_port")
            self.ws_server_port = __config.get("ws_port")


config = Config()
