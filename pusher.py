import json
from datetime import datetime, timezone
import requests
import pytz

from config import DISCORD_PUSH_CHANNEL_ID, DISCORD_PUSH_WEBHOOK_SECRET


async def send_discord_message(title: str, message: str, level: str = "info", fields: list = None):
    match level:
        case "info":
            color = 1926125
        case "warning":
            color = 16776960
        case "error":
            color = 14680064
        case "success":
            color = 65280
        case _:
            color = 1926125
    request_json = {
            "content": None,
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": color,
                    "fields": fields if fields else [],
                    "author": {
                        "name": f"DGP-Bot {level.capitalize()} Message",
                        "icon_url": "https://avatars.githubusercontent.com/in/268880"
                    },
                    "timestamp": datetime.now(timezone.utc).astimezone(pytz.timezone('Asia/Shanghai')).isoformat()
                }
            ],
            "username": "DGP-Bot",
            "avatar_url": "https://avatars.githubusercontent.com/in/268880",
            "attachments": []
        }
    rep = requests.post(
        url=f"https://discord.com/api/webhooks/{DISCORD_PUSH_CHANNEL_ID}/{DISCORD_PUSH_WEBHOOK_SECRET}",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json=request_json
    )
    if rep.status_code != 204:
        print(f"推送执行错误：{rep.text}")
    else:
        print(f"推送结果：HTTP {rep.status_code} Success")
