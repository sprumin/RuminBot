from slacker import Slacker

import asyncio
import json
import settings
import websocket
import websockets


# slack module setting
slack = Slacker(settings.RUMIN_TOKEN)

# slack rtm setting
response = slack.rtm.start()
sock_endpoint = response.body["url"]

async def execute_bot():
    ws = await websockets.connect(sock_endpoint)

    while True:
        message_json = await ws.recv()
        print(message_json)

loop = asyncio.get_event_loop()
loop.run_until_complete(execute_bot())
loop.run_forever()
