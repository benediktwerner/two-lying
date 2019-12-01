#!/usr/bin/env python3

import json
import os

import aiohttp
from aiohttp import web

from game_server import server, ReloadException, NoReloadException


PORT = int(os.environ.get("PORT", "8080"))


def redirect_handler(target):
    async def handler(request):
        raise web.HTTPFound(target)

    return handler


async def socket_handler(request):
    ws = web.WebSocketResponse(heartbeat=10)
    await ws.prepare(request)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == "close":
                    await ws.close()
                else:
                    try:
                        await server.handle_socket_msg(ws, msg.data)
                    except ReloadException as e:
                        print("Error during msg handling:")
                        print(e.args[0])
                        await ws.send_str(json.dumps({"error": e.args[0], "reload": True}))
                    except NoReloadException as e:
                        print("Error during msg handling:")
                        print(e.args[0])
                        await ws.send_str(json.dumps({"error": e.args[0]}))
                    except Exception as e:
                        print("Unhandled exception during msg handling:")
                        print(e)
                        await ws.send_str(json.dumps({"error": "Internal error"}))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"Websocket closed with exception {ws.exception()}")
    finally:
        await server.disconnect_socket(ws)
        print("Websocket closed")

    return ws


async def crate_room_handler(request):
    room_id = server.create_room()
    return web.json_response({"roomId": room_id})


async def can_join_room_handler(request):
    name = request.rel_url.query.get("name")
    room_id = request.rel_url.query.get("roomId")
    can_join, reason = server.can_join_room(name, room_id)
    return web.json_response({"canJoin": can_join, "reason": reason})


app = web.Application()
app.add_routes(
    [
        web.get("/", redirect_handler("/index.html")),
        web.post("/create_room", crate_room_handler),
        web.get("/can_join_room", can_join_room_handler),
        web.get("/socket", socket_handler),
        web.static("/", "static"),
    ]
)

web.run_app(app, port=PORT)
