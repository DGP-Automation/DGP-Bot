import requests
import json


def get_log(device_id: str) -> dict | None:
    url = f"https://homa.snapgenshin.com/HutaoLog/ByDeviceId?id={device_id}"
    headers = {
        "authority": "dgp-bot"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None
