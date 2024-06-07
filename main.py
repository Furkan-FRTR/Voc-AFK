import sys
import json
import time
import requests
import asyncio
import websocket
import ssl
from flask import Flask
from threading import Thread

app = Flask(__name__)

# GUILD_ID est l'identifiant du serveur 
GUILD_ID = 6546545645641141
# CHANNEL_ID est l'identifiant du canal vocal.
CHANNEL_ID = 555485151147141
# Votre token va entre les crochets.
usertoken = "ton token ici"

# Ne pas changer, sauf si vous voulez vous mettre en mode hors ligne, ou désactiver le mode muet et sourdine
# (il est déjà configuré pour être en mode muet et sourdine et en ligne).
status = "online"
SELF_MUTE = True
SELF_DEAF = True

# Ne pas modifier by fr41tr42 
headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers)
if validate.status_code != 200:
    print("[ERROR] Votre token pourrait être invalide. Veuillez le vérifier.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

def joiner(token, status):
    try:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
        start = json.loads(ws.recv())
        heartbeat = start['d']['heartbeat_interval']
        auth = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "Windows 10",
                    "$browser": "Google Chrome",
                    "$device": "Windows"
                },
                "presence": {
                    "status": status,
                    "afk": False
                }
            },
            "s": None,
            "t": None
        }
        vc = {
            "op": 4,
            "d": {
                "guild_id": GUILD_ID,
                "channel_id": CHANNEL_ID,
                "self_mute": SELF_MUTE,
                "self_deaf": SELF_DEAF
            }
        }
        ws.send(json.dumps(auth))
        ws.send(json.dumps(vc))
        time.sleep(heartbeat / 1000)
        ws.send(json.dumps({"op": 1, "d": None}))
    except ssl.SSLEOFError as e:
        print(f"SSL error: {e}")
    except websocket.WebSocketException as e:
        print(f"WebSocket error: {e}")
    finally:
        ws.close()

def run_joiner():
    print(f"Connecté en tant que {username}#{discriminator} ({userid}).")
    while True:
        joiner(usertoken, status)
        time.sleep(30) 

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    userinfo = requests.get('https://discordapp.com/api/v9/users/@me',
                            headers={"Authorization": usertoken, "Content-Type": "application/json"}).json()
    username = userinfo["username"]
    discriminator = userinfo["discriminator"]
    userid = userinfo["id"]
    
    keep_alive()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_joiner())

run_joiner()
