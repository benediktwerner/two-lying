#!/usr/bin/env python3

import os

import aiohttp
from aiohttp import web

import ws_handler


PORT = int(os.environ.get("PORT", "8080"))


def redirect_handler(target):
    async def handler(request):
        raise web.HTTPFound(target)

    return handler


async def socket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                await ws_handler.handle(ws, msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(f"Websocket closed with exception {ws.exception()}")

    await ws_handler.disconnect(ws)
    print("Websocket closed")
    return ws


app = web.Application()
app.add_routes(
    [
        web.get("/", redirect_handler("/index.html")),
        web.get("/socket", socket_handler),
        web.static("/", "static"),
    ]
)

web.run_app(app, port=PORT)
