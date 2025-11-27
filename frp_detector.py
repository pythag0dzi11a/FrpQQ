import datetime
import json

import aiohttp

from config import config


class FrpStatus:
    """
    FRP状态类，包含多个FRP代理的状态信息。
    Attributes:
        all_items (dict): 包含FRP代理名称和对应FrpItem对象的字典。
    Methods:
        generate_items(): 根据传入的元数据生成FrpItem对象并存储在items字典中。
        get_time(name: str): 获取指定代理的启动和关闭时间。
        get_status(name: str): 获取指定代理的当前状态。
    """

    def __init__(self, meta_data: dict):
        self.__proxies_list = meta_data.get("proxies", [])
        self.all_items = {}
        self._generate_items()

    def _generate_items(self):
        for proxy in self.__proxies_list:
            name = proxy.get("name", "")
            status = proxy.get("status", "")
            start_time = proxy.get("last_start", "")
            close_time = proxy.get("last_close", "")

            self.all_items[name] = FrpItem(name, status, start_time, close_time)

    def get_time(self, name: str):
        item: FrpItem = self.all_items[name]  # 没有使用.get 可能导致些未知错误。
        print(f"Fetching {name} time.")
        return {"start_time": item.start_time, "close_time": item.close_time}

    def get_status(self, name: str) -> str:
        item: FrpItem = self.all_items[name]
        print(f"Fetching {name} status.")
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
            self.old_status: FrpStatus | None = await self.get_tcp_status()
            print("First initialization of FRP status.")
            return {}
        else:
            new_status: FrpStatus | None = await self.get_tcp_status()
            diff = {}
            if not new_status:
                print("Failed to fetch new FRP status.")
                return {}

            else:
                for name, frpItem in self.old_status.all_items:
                    if new_status.get_status(name) != frpItem.status:
                        diff[name] = {
                            "old_status": frpItem.status,
                            "new_status": new_status.get_status(name),
                            "check_time": datetime.datetime.now()
                        }
                print(f"Differences found: {diff}")
                self.old_status = new_status
                return diff
