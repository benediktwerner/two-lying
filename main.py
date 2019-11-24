#!/usr/bin/env python3

import aiohttp
from aiohttp import web

import ws_handler


async def socket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    ws_handler.sockets.append(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                await ws_handler.handle(ws, msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f"Websocket closed with exception {ws.exception()}")

    ws_handler.sockets.remove(ws)
    print("Websocket closed")
    return ws


app = web.Application()
app.add_routes(
    [
        web.static("/", "index.html"),
        web.static("/index.js", "index.js"),
        web.get("/socket", socket_handler),
    ]
)

web.run_app(app)
