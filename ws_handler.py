import json
import random

players = []
current_player = None
word = None


async def send_update():
    ps = [
        {
            "name": p["name"],
            "points": p["points"],
            "status": p["status"] if p["ws"] is not None else "disconnected",
        }
        for p in players
    ]
    any_disconnected = any(p["ws"] is None for p in players)
    for i, p in enumerate(players):
        if p["ws"] is None:
            continue
        data = {
            "players": ps,
            "you": {"index": i, "word": p["word"]},
            "waiting": current_player is None or any_disconnected,
            "word": word,
        }
        await p["ws"].send_str(json.dumps(data))


async def handle(ws, msg):
    global players, current_player, word

    if not msg:
        return

    msg = json.loads(msg)
    msg_type, msg_data = msg["type"], msg["data"]

    if msg_type == "login":
        name = msg_data
        for p in players:
            if p["name"] == name:
                if p["ws"] is not None:
                    await ws.close()
                    return
                p["ws"] = ws
                break
        else:
            players.append(
                {"ws": ws, "name": name, "points": 0, "status": "ready", "word": None}
            )
    elif msg_type == "start-game":
        for p in players:
            if p["ws"] is None:
                current_player = None
                break
        players = [p for p in players if p["ws"] is not None]
        next_round()
    elif msg_type == "set-word":
        index = msg_data["index"]
        players[index]["word"] = msg_data["word"]
    elif msg_type == "ready":
        players[msg_data]["status"] = "ready"
    elif msg_type == "not-ready":
        players[msg_data]["status"] = "not-ready"
    elif msg_type == "guess":
        players[msg_data]["points"] += 1
        if word == players[msg_data]["word"]:
            players[current_player]["points"] += 1
        next_round()
    elif msg_type == "choose-word":
        p = random.choice([p for p in players if p["status"] != "guesser"])
        word = p["word"]
    else:
        print("Unknown message type:", msg_type)
        return

    await send_update()


def next_round():
    global players, current_player, word

    if current_player is None:
        current_player = 0
    else:
        current_player = (current_player + 1) % len(players)

    word = None
    for i, p in enumerate(players):
        p["word"] = None

        if i == current_player:
            p["status"] = "guesser"
        else:
            p["status"] = "not-ready"


async def disconnect(ws):
    global players, current_player, word

    for p in players:
        if p["ws"] == ws:
            p["ws"] = None
            break
    else:
        return

    for p in players:
        if p["ws"] is not None:
            await send_update()
            return

    players = []
    current_player = None
    word = None
