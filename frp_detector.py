import json

import aiohttp

from config import config


class FrpDetector:
    def __init__(self):
        self.first_run = True
        self.old_map = {}
        self.now_map = {}

        self.past_proxies_list = []
        self.now_proxies_list = []

    async def compare_proxies(self) -> dict:
        if self.old_map == {} and self.first_run:
            self.first_run = False
        else:
            self.old_map = self.now_map.copy()
            self.now_map = {}

        proxies_list = await self.get_proxies_list()

        self.now_map = {item.get("name"): item.get("status") for item in proxies_list}
        print(self.now_map)
        print(self.old_map)

        changes = {}

        for name, status in self.now_map.items():
            old_status = self.old_map.get(name)
            print(old_status)
            if old_status is None:
                continue  # New proxy, no previous status to compare
            if status != old_status:
                changes[name] = (old_status, status)

        print(changes)
        return changes

    async def update_proxies_list(self):
        if self.past_proxies_list == []:
            pass
        else:
            self.past_proxies_list = self.now_proxies_list
            self.now_proxies_list = []

        proxies_list = await self.get_proxies_list()

        for single_proxy in proxies_list:
            name = single_proxy.get("name")
            status = single_proxy.get("status")

            if status == "online":
                port = single_proxy.get("conf").get("remotePort")
            else:
                port = None

            self.now_proxies_list.append(
                {
                    "name": name,
                    "status": status,
                    "port": port,
                }
            )

    async def get_proxies_list(self) -> list:
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
