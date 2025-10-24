import asyncio
import json

import aiohttp

with open('config.json', 'r') as f:
    user_name = json.load(f).get("user-name")
    passwd = json.load(f).get("password")

async def main():
    url = "https://frp.pythagodzilla.top/api/proxy/tcp"
    auth = aiohttp.BasicAuth("pythagodzilla", "@Jtbx2mtblj")

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(url) as response:
            if response.status == 200:
                api_data = json.loads(await response.text())

asyncio.run(main())