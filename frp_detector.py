import datetime
import json

import aiohttp

from config import config


# class FrpDetector:
#     def __init__(self):
#         self.__first_init = True
#         self.old_map = {}
#         self.now_map = {}
#
#         self.past_proxies_list = []
#         self.now_proxies_list = []
#
#     @staticmethod
#     async def format_proxies_list_to_dict(data: list) -> dict:
#         return {item.get("name"): item.get("status") for item in data}
#
#     async def compare_proxies(self) -> dict:
#
#         if self.__first_init:
#             self.now_map = await self.format_proxies_list_to_dict(
#                 await self.get_proxies_list()
#             )  # 异步函数没法用lambda.
#             print("First init completed.")
#             self.__first_init = False
#
#         self.old_map = self.now_map.copy()
#
#         self.now_map = await self.format_proxies_list_to_dict(
#             await self.get_proxies_list()
#         )
#         print(self.now_map)
#         print(self.old_map)
#
#         changes = {}
#         for name, now_status in self.now_map.items():
#             old_status = self.old_map.get(name)
#
#             if now_status != old_status:
#                 changes[name] = (old_status, now_status)
#
#         print(changes)
#         return changes
#
#     @staticmethod
#     async def get_proxies_list() -> list:
#         url = "https://frp.pythagodzilla.top/api/proxy/tcp"
#         auth = aiohttp.BasicAuth(config.user_name, config.password)
#
#         async with aiohttp.ClientSession(auth=auth) as session:
#             async with session.get(url) as response:
#                 if response.status == 200:
#                     api_data = json.loads(await response.text())
#                     proxies_list = api_data.get("proxies")
#                     print(proxies_list[0].get("status"))
#                 else:
#                     proxies_list = []
#         print(proxies_list)
#         return proxies_list

class FrpStatus:
    def __init__(self, meta_data: dict):
        self.__proxies_list = meta_data.get("proxies", [])
        self.items = {}
        self.generate_items()

    def generate_items(self):
        for proxy in self.__proxies_list:
            name = proxy.get("name", "")
            status = proxy.get("status", "")
            start_time = proxy.get("last_start", "")
            close_time = proxy.get("last_close", "")

            self.items[name] = FrpItem(name, status, start_time, close_time)

    # def traversal_status(self):
    #     for name, item in self.items.items():
    #         yield {"name": name, "status": item.status}

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


class FrpDetector:
    def __init__(self):
        self.base_url = "https://frp.pythagodzilla.top/api"
        self.old_status: FrpStatus | None = None

    async def get_tcp_status(self) -> FrpStatus | None:
        """
        通过FRP的API获取当前TCP代理的状态。
        If failed, return None.
        通过Basic Auth进行认证，使用config中的用户名和密码。
        访问"/proxy/tcp"端点，获取代理状态的JSON数据。
        :return: FrpStatus对象，包含代理状态信息；如果请求失败则返回None。
        :rtype: FrpStatus | None
        """
        url = self.base_url + "/proxy/tcp"
        auth = aiohttp.BasicAuth(config.username, config.password)
        try:
            async with aiohttp.ClientSession(
                    auth=auth
            ) as session:
                async with session.get(url) as response:

                    if response.status == 200:
                        api_data = json.loads(await response.text())
                        return FrpStatus(api_data)
                    else:
                        return None
        except Exception as e:
            print(f"Error fetching FRP status: {e}")
            return None

    async def compare_diff(self) -> dict:
        """
        比较当前FRP代理状态与上一次记录的状态，找出状态变化的代理。
        如果是第一次调用该方法，则初始化旧状态并返回空字典。

        eg：{"proxy1": {"old_status": "online", "new_status": "offline", "check_time": datetime.datetime(...)}}。

        代理名称为键，值为包含旧状态、新状态和检查时间的字典。
        代理状态变化包括从"online"变为"offline"或从"offline"变为"online"。
        变化时间使用datetime.datetime.now()获取当前时间。
        变化的代理会被记录在返回的字典中。
        :return: 包含状态变化代理信息的字典，格式为 {代理名称: {"old_status": 旧状态, "new_status": 新状态, "check_time": 检查时间}}。
        """
        if not self.old_status:
            self.old_status = await self.get_tcp_status()
            print("First initialization of FRP status.")
            return {}
        else:
            new_status = await self.get_tcp_status()
            diff = {}
            if not new_status:
                print("Failed to fetch new FRP status.")
                return {}

            else:
                for name, status in self.old_status.items.items():
                    if new_status.get_status(name) != status.status:
                        diff[name] = {
                            "old_status": status.status,
                            "new_status": new_status.get_status(name),
                            "check_time": datetime.datetime.now()
                        }
                return diff
