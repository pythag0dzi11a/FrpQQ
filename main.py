import asyncio
import logging
import hashlib
import schedule
import aiohttp

from frp_detector import FrpDetector
from message import Message
from message_sender import MessageSender
from type_definition import *
from config import config

frp_detector = FrpDetector()

notification_person = "1670671958"

msg_sender = MessageSender()


async def webui_interaction():
    uri = f"http://{config.napcat_server_addr}:{config}/api/auth/login"
    hash_token = hashlib.sha256(
        f"{config.webui_token}.napcat".encode()
    ).hexdigest()  # 如果做指数退避，hash计算需要摘除。
    async with aiohttp.ClientSession() as session:
        async with session.post(uri, json={"hash": hash_token}) as resp:
            if resp.status == 200:
                return True
            else:
                return False


def gen_msg(change_proxies: dict) -> Message:
    msg: str = "以下代理状态发生变化：\n"
    for name, (old_status, new_status) in change_proxies.items():
        msg += f"{name}: {"在线" if old_status == "online" else "离线"}->{"在线" if new_status == "online" else "离线"}\n"

    return Message(Text(text=msg))


async def detect_changes():
    print("Start run")
    changes_dict = await frp_detector.compare_proxies()
    if not changes_dict:
        return
    else:
        message = gen_msg(changes_dict)

        await msg_sender.send_private_message(
            user_id=notification_person, message=message
        )


try:
    schedule.every(15).seconds.do(lambda: asyncio.run(detect_changes()))

    while True:
        schedule.run_pending()

except Exception as e:
    print(f"An error occurred: {e}")
    logging.exception(e)
