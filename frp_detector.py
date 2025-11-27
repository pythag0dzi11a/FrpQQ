import datetime
import json

import aiohttp

from config import config


class FrpItem:
    """
    FRP代理项类，表示单个FRP代理的状态信息。
    Attributes:
        name (str): 代理名称。
        status (str): 代理状态（如"online"或"offline"）。
        start_time (str): 代理的最后启动时间。
        close_time (str): 代理的最后关闭时间。
        final_dict (dict): 包含代理信息的字典表示形式。
        """

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


class FrpStatus:
    """
    FRP状态类，包含多个FRP代理的状态信息。
    本身是个FrpItem组成的dict。Key是代理名称，Value是FrpItem对象。
    Attributes:
        all_items (dict): 包含FRP代理名称和对应FrpItem对象的字典。
    Methods:
        generate_items(): 根据传入的元数据生成FrpItem对象并存储在items字典中。
        get_time(name: str): 获取指定代理的启动和关闭时间。
        get_status(name: str): 获取指定代理的当前状态。
    """

    def __init__(self):
        self.all_items = {}

    def generate_items_by_primitive_data(self, meta_data: dict):
        proxies_list = meta_data.get("proxies", [])
        if proxies_list:
            for proxy in proxies_list:
                name = proxy.get("name", "")
                status = proxy.get("status", "")
                start_time = proxy.get("last_start", "")
                close_time = proxy.get("last_close", "")

                self.all_items[name] = FrpItem(name, status, start_time, close_time)
        else:
            self.all_items = {}

    def add_item(self, item: FrpItem):
        self.all_items[item.name] = item

    def get_time(self, name: str):
        # item: FrpItem = self.all_items[name]  # 没有使用.get 可能导致些未知错误。
        item: FrpItem = self.all_items.get(name)
        print(f"Fetching {name} time.")
        return {"start_time": item.start_time, "close_time": item.close_time}

    def get_status(self, name: str) -> str | None:
        # item: FrpItem = self.all_items[name]
        item: FrpItem = self.all_items.get(name)
        print(f"Fetching {name} status.", item.status)
        return item.status


class FrpDifferenceItem:
    """
    FRP差异项类，用于表示FRP代理状态的变化信息。
    Attributes:
        name (str): 代理名称。
        old_status (str): 旧的代理状态。
        new_status (str): 新的代理状态。
        check_time (datetime.datetime): 检查时间。
    """

    def __init__(self, name: str, old_status: str, new_status: str, is_new: bool = False):
        self.name = name
        self.is_new: bool = is_new
        self.old_status = old_status
        self.new_status = new_status
        self.check_time = datetime.datetime.now()


class FrpDifference:
    """
    FRP差异类，用于表示FRP代理状态的变化。

    """

    def __init__(self):
        self.all_diffs = {}
        super().__init__()

    def add_diff_item(self, item: FrpDifferenceItem):
        self.all_diffs[item.name] = item


class FrpDetector:
    """
    FRP检测器类，用于监控FRP代理的状态变化。
    Attributes:
        base_url (str): FRP API的基础URL。
        old_status (FrpStatus | None): 上一次记录的FRP代理状态。
    Methods:
        get_tcp_status(): 获取当前TCP代理的状态。理论为private方法。
        compare_diff(): 比较当前状态与上一次状态，找出状态变化的代理
    """

    def __init__(self):
        self.base_url = "https://frp.pythagodzilla.top/api"
        self.old_status: FrpStatus | None = None

    @classmethod
    async def create(cls):
        inst = cls()
        await inst._init_frp_status()
        return inst

    async def _init_frp_status(self):
        """
        暂时性的初始化方法，由于现在只需要监控tcp proxies，所以此处的实现暂时直接使用get_tcp_status方法。
        未来如果需要监控其他类型的代理，可以在此方法中添加相应的初始化逻辑。
        """
        try:
            self.old_status: FrpStatus = await self.get_tcp_status()
        except Exception as e:
            print(f"Error initializing FRP status: {e}")
            self.old_status = FrpStatus()

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
        auth = aiohttp.BasicAuth(config.user_name, config.password)
        try:
            async with aiohttp.ClientSession(
                    auth=auth
            ) as session:
                async with session.get(url) as response:

                    if response.status == 200:
                        api_data = json.loads(await response.text())
                        result: FrpStatus = FrpStatus()
                        print("Successfully fetched FRP TCP status.")
                        print(f"{api_data}")
                        result.generate_items_by_primitive_data(api_data)
                        return result
                    else:
                        return None
        except Exception as e:
            print(f"Error fetching FRP status: {e}")
            return None

    async def compare_diff(self) -> FrpDifference:
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
            return FrpDifference()

        new_status: FrpStatus | None = await self.get_tcp_status()
        diff = FrpDifference()

        if not new_status:
            print("Failed to fetch new FRP status.")
            return FrpDifference()

        print("Comparing old and new FRP statuses.")
        for name, frpItem in new_status.all_items.items():
            if not self.old_status.get_status(name):
                print("New proxy detected:", name)
                diff.add_diff_item(
                    FrpDifferenceItem(frpItem.name, self.old_status.get_status(name), frpItem.status,
                                      is_new=True))

            elif self.old_status.get_status(name) != frpItem.status:
                print("Status change detected for proxy:", name)
                diff.add_diff_item(
                    FrpDifferenceItem(frpItem.name, self.old_status.get_status(name), frpItem.status,
                                      is_new=False))
        print(f"Differences found: {diff.all_diffs}")
        self.old_status = new_status
        return diff
