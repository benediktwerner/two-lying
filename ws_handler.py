import json


sockets = []


async def send(ws, data):
    # await ws.send_str(json.dumps(data))
    await ws.send_str(data)


async def send_all(data):
    for ws in sockets:
        send(ws, data)


async def handle(ws, msg):
    if not msg:
        return
    
    send(ws, "Echo: " + msg)

    # if msg[0] == "!":
    #     msg = json.loads(msg[1:])
    #     msg_type, msg_data = msg["type"], msg["data"]

    #     if msg_type not in DM_HANDLERS:
    #         await send(ws, f"Error: Invalid msg type '{msg_type}'")
    #         return

    #     await DM_HANDLERS[msg_type](ws, **msg_data)
    #     return
