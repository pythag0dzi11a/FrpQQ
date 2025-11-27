import hashlib
import json

import aiohttp

from config import config
from message import Message


class WebUIInteraction:
    def __init__(self):
        # noinspection HttpUrlsUsage
        self.base_uri = f"http://{config.napcat_server_addr}:{config}"
        self.hash_token = hashlib.sha256(
            f"{config.webui_token}.napcat".encode()
        ).hexdigest()  # 如果做指数退避，hash计算需要摘除。
        self.header = {}

    async def webui_login(self) -> bool:
        uri = self.base_uri + "/api/auth/login"
        async with aiohttp.ClientSession() as session:
            async with session.post(uri, json={"hash": self.hash_token}) as resp:
                if resp.status == 200:
                    self.header = {"Authorization": f"Bearer {await resp.text()}"}
                    return True
                else:
                    return False


class MessageSender:
    def __init__(self, http_port: int = 3000, http_token: str = ""):
        self._http_port = http_port
        self._http_token = http_token
        webui_interaction = WebUIInteraction()
        self.header = webui_interaction.webui_login()

    async def send_private_message(self, message: Message, user_id: str):
        # noinspection HttpUrlsUsage
        url = f"http://{config.napcat_server_addr}:{self._http_port}/send_private_msg"

        gen_message = message.to_list()

        # request_body 是个dict，其中message是个list。
        request_body = {
            "user_id": user_id,
            "message": gen_message,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=json.dumps(request_body)) as resp:
                    text = await resp.text()
                    print(text)
        except Exception as e:
            print(f"Send message failed: {e}")
