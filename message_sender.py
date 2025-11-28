import hashlib
import json

import aiohttp

from config import config
from message import Message


class WebUIInteraction:
    def __init__(self):
        # noinspection HttpUrlsUsage
        self.base_uri = f"http://{config.napcat_server_addr}:{config.webui_port}"
        self.hash_token = hashlib.sha256(
            f"{config.webui_token}.napcat".encode()
        ).hexdigest()  # 如果做指数退避，hash计算需要摘除。
        self.header = {}

    async def webui_login(self) -> bool:
        uri = self.base_uri + "/api/auth/login"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(uri, json={"hash": self.hash_token}) as resp:
                    if resp.status == 200:
                        auth_code = await resp.json()
                        self.header = {"Authorization": f"Bearer {auth_code.get("data").get("Credential")}"}
                        status = await self.check_login_status()
                        if status:
                            print("WebUI login successful.")
                            print(f"Headers: {self.header}")
                            return True
                        else:
                            print("WebUI login failed.")
                            return False
                    else:
                        print("WebUI login failed.")
                        return False
        except Exception as e:
            print(f"WebUI login exception: {e}")
            return False

    async def check_login_status(self) -> bool:
        uri = self.base_uri + "/api/QQLogin/CheckLoginStatus"
        print(f"Check headers: {self.header}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(uri, headers=self.header) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        print(f"WebUI check login status response: {response}")
                        if response.get("data").get("isLogin"):
                            print("WebUI login status: Logged in.")
                            return True
                        else:
                            print("WebUI login status: Not logged in.")
                            return False
                    else:
                        print("WebUI login status: Not logged in.")
                        return False
        except Exception as e:
            print(f"WebUI check login status exception: {e}")
            return False


class MessageSender:

    @classmethod
    async def create(cls, http_port: int = config.http_server_port, http_token: str = ""):
        inst = cls()
        webui_interaction = WebUIInteraction()
        cls._http_port = http_port
        cls._http_token = http_token
        await webui_interaction.webui_login()
        return inst

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
