# oh yeah i hate myself how could you tell

import json
import requests

with open("settings.json", "r") as f:
    settings = json.loads(f.read())

API = f"https://api.telegram.org/bot{settings["token"]}"
VERSION = "1.0-alpha1-telegram"

def sendmessage(message: str, channelid: int) -> int:
        sentmessage = requests.post(f"{API}/sendMessage", json={ "chat_id": channelid, "text": message})
        return sentmessage.status_code

offset = 0
while True:
    update = requests.get(f"{API}/getUpdates", json={ "offset": offset, "timeout": 100, "allowed_updates": "message"})
    offset = update.json()["result"][-1]["update_id"]+1
    messageinfo = update.json()["result"][-1]["message"]

    match messageinfo["text"]:
        case "/help":
            sendmessage("/help\n/ping\n/version", messageinfo["chat"]["id"])
        case "/ping":
            sendmessage(f"Pong! @{messageinfo["from"]["first_name"]}", messageinfo["chat"]["id"])
        case "/version":
            sendmessage(VERSION, messageinfo["chat"]["id"])
