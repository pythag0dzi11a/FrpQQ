import asyncio
import logging

# noinspection PyPackageRequirements
import schedule

from frp_detector import FrpDetector, FrpDifference
from message import Message, Text
from message_sender import MessageSender

# Configuration part
frp_detector = asyncio.run(FrpDetector.create())
notification_person = "1670671958"
msg_sender = MessageSender()


def gen_msg(change_proxies: FrpDifference) -> Message:
    msg: str = "以下代理状态发生变化：\n"
    for name, item in change_proxies.all_diffs.items():
        if item.is_new:
            msg += f"{name}: 新增代理，当前状态：{'在线' if item.new_status == 'online' else '离线'}\n"
        else:
            msg += f"{name}: {'在线' if item.old_status == 'online' else '离线'}->{'在线' if item.new_status == 'online' else '离线'}\n"

    return Message(Text(text=msg))


async def detect_changes():
    print("Start detect changes.")
    changes: FrpDifference = await frp_detector.compare_diff()
    if not changes.all_diffs:
        return
    else:
        message = gen_msg(changes)

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
