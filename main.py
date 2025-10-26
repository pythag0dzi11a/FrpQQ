import asyncio

import schedule

from message import Message
from qq_message_poster import QQMessagePoster
from frp_detector import FrpDetector
from type_definition import *

frp_detector = FrpDetector()

notification_person = "1670671958"

message_poster = QQMessagePoster()

# message = Message()
# asyncio.run(
#     message_poster.send_private_message(user_id=notification_person, message=message)
# )


def detect_changes():
    print("Start run")
    changes = asyncio.run(frp_detector.compare_proxies())
    if changes == {}:
        return
    else:
        msg: str = "以下代理状态发生变化：\n"
        for name, (old_status, new_status) in changes.items():
            msg += f"{name}: {old_status} -> {new_status}\n"
        message = Message(Text(text=msg))
        asyncio.run(
            message_poster.send_private_message(
                user_id=notification_person, message=message
            )
        )

try:
    schedule.every(15).seconds.do(detect_changes)

    while True:
        schedule.run_pending()

except Exception as e:
    print(f"An error occurred: {e}")