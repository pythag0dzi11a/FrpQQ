import json

import aiohttp

from config import config


class FrpDetector:
    def __init__(self):
        self.first_init = True
        self.old_map = {}
        self.now_map = {}

        self.past_proxies_list = []
        self.now_proxies_list = []

    @staticmethod
    async def format_proxies_list_to_dict(data: list) -> dict:
        return {item.get("name"): item.get("status") for item in data}

    async def compare_proxies(self) -> dict:

        if self.first_init:
            self.now_map = await self.format_proxies_list_to_dict(
                await self.get_proxies_list()
            )  # 异步函数没法用lambda.
            print("First init completed.")
            self.first_init = False

        self.old_map = self.now_map.copy()

        self.now_map = await self.format_proxies_list_to_dict(
            await self.get_proxies_list()
        )
        print(self.now_map)
        print(self.old_map)

        changes = {}

        for name, now_status in self.now_map.items():
            old_status = self.old_map.get(name)

            if now_status != old_status:
                changes[name] = (old_status, now_status)

        print(changes)
        return changes

    @staticmethod
    async def get_proxies_list() -> list:
        url = "https://frp.pythagodzilla.top/api/proxy/tcp"
        auth = aiohttp.BasicAuth(config.user_name, config.password)

        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    api_data = json.loads(await response.text())
                    proxies_list = api_data.get("proxies")
                    print(proxies_list[0].get("status"))
                else:
                    proxies_list = []
        print(proxies_list)
        return proxies_list


class FrpStatus:
    def __init__(self, meta_data: dict):
        self.__proxies_list = meta_data.get("proxies", [])
        self.items = {}

    def generate_items(self):
        for proxy in self.__proxies_list:
            name = proxy.get("name", "")
            status = proxy.get("status", "")
            start_time = proxy.get("last_start", "")
            close_time = proxy.get("last_close", "")

            self.items[name] = FrpItem(name, status, start_time, close_time)

    def get_time(self, name: str):
        item: FrpItem = self.items[name]  # 没有使用.get 可能导致些未知错误。
        return {"start_time": item.start_time, "close_time": item.close_time}

    def get_status(self, name: str) -> str:
        item: FrpItem = self.items[name]
        return item.status


class FrpItem:
    def __init__(self, name: str, status: str, start_time: str, close_time: str):
        self.name = name
        self.status = status
        self.start_time = start_time
        self.close_time = close_time

        self.final_dict = {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time,
            "close_time": self.close_time,
        }
