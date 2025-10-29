import json

import aiohttp

from config import config
from message import Message


class MessageSender:
    def __init__(self):
        pass

    @staticmethod
    async def send_private_message(message: Message, user_id: str):
        url = f"http://{config.napcat_server_addr}:{config.http_server_port}/send_private_msg"

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
