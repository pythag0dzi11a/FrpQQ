import json

import aiohttp

from config import config
from message import Message


class MessageSender:
    def __init__(self, http_port: int = 3000, http_token: str = ""):
        self._http_port = http_port
        self._http_token = http_token

    async def send_private_message(self, message: Message, user_id: str):
        # noinspection HttpUrlsUsage
        url = f"http://{config.napcat_server_addr}:{self._http_port}/send_private_msg"

        gen_message = message.to_list()

        # request_body 是个dict，其中message是个list。
        request_body = {
            "user_id": user_id,
            "message": gen_message,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=json.dumps(request_body)) as resp:
                text = await resp.text()
                print(text)
