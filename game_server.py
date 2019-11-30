import json
import random


ROOM_ID_ALPHABET = "abcdefghkmnopqrstuvwxyz1234567890"


class ReloadException(Exception):
    pass


class NoReloadException(Exception):
    pass


class Player:
    def __init__(self, name, ws):
        self.name = name
        self.ws = ws
        self.points = 0
        self.word = None
        self.status = "not-ready"

    def to_json(self, waiting):
        if waiting:
            status = "disconnected" if self.ws is None else "ready"
        else:
            status = self.status
        return {"name": self.name, "points": self.points, "status": status}


class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []
        self.current_player = None
        self.word = None

    def can_join(self, name):
        for p in self.players:
            if p.name == name and p.ws is not None:
                return False
        return True

    async def send_updates(self):
        any_disconnected = any(p.ws is None for p in self.players)
        waiting = self.current_player is None or any_disconnected
        ps = [p.to_json(waiting) for p in self.players]
        for i, p in enumerate(self.players):
            if p.ws is None:
                continue
            data = {
                "players": ps,
                "roomId": self.room_id,
                "you": {"index": i, "word": p.word},
                "waiting": waiting,
                "word": self.word,
            }
            await p.ws.send_str(json.dumps(data))

    async def join(self, ws, name):
        for p in self.players:
            if p.name == name:
                if p.ws is None:
                    p.ws = ws
                    break
                return False
        else:
            self.players.append(Player(name, ws))

        await self.send_updates()

        return True

    def get_player(self, ws):
        for p in self.players:
            if p.ws is ws:
                return p
        return None

    async def handle_socket_msg(self, ws, msg_type, msg_data):
        player = self.get_player(ws)

        if msg_type == "start-game":
            for p in self.players:
                if p.ws is None:
                    self.current_player = None
                    break
            self.players = [p for p in self.players if p.ws is not None]
            if len(self.players) < 3:
                raise NoReloadException("Too few players")
            self.next_round()
        elif msg_type == "set-word":
            player.word = msg_data["word"]
        elif msg_type == "ready":
            player.status = "ready"
        elif msg_type == "not-ready":
            player.status = "not-ready"
        elif msg_type == "guess":
            index = msg_data["index"]
            self.players[index].points += 1
            self.players[index].word = None
            if self.word == self.players[index].word:
                self.players[self.current_player].points += 1
            self.next_round()
        elif msg_type == "choose-word":
            p = random.choice([p for p in self.players if p.status != "guesser"])
            self.word = p.word
        else:
            raise NoReloadException(f"Unknown message type: {msg_type}")

        await self.send_updates()

    def next_round(self):
        if self.current_player is None:
            self.current_player = 0
        else:
            self.current_player = (self.current_player + 1) % len(self.players)

        self.word = None
        for i, p in enumerate(self.players):
            if i == self.current_player:
                p.status = "guesser"
            else:
                p.status = "not-ready"

    async def disconnect_socket(self, ws):
        for p in self.players:
            if p.ws is ws:
                p.ws = None
                await self.send_updates()
                return

    def is_empty(self):
        return all(p.ws is None for p in self.players)


class Server:
    def __init__(self):
        self.rooms = {}
        self.sockets = {}

    def create_room(self):
        while True:
            room_id = "".join(random.choice(ROOM_ID_ALPHABET) for _ in range(6))
            if room_id not in self.rooms:
                self.rooms[room_id] = Room(room_id)
                return room_id

    def can_join_room(self, name, room_id):
        if not name or not room_id:
            return False, "Missing name or room id"

        room = self.rooms.get(room_id)
        if room is None:
            return False, f"No room with id '{room_id}'"

        if not room.can_join(name):
            return False, f"The room already has a player with name '{name}'"

        return True, None

    async def handle_socket_msg(self, ws, msg):
        if not msg:
            raise NoReloadException(f"Empty request")

        try:
            msg = json.loads(msg)
        except Exception as e:
            print("Exception during json parsing:", e)
            raise NoReloadException(f"Invalid json request body: {msg}")

        msg_type, msg_data = msg.get("type"), msg.get("data")
        if msg_type == "join":
            name = msg_data.get("name")
            room_id = msg_data.get("roomId")
            if not name or not room_id:
                raise ReloadException(f"Invalid join request: {msg}")

            room = self.rooms.get(room_id)
            if room is None:
                room = Room(room_id)
                self.rooms[room_id]= room

            joined = await room.join(ws, name)
            if not joined:
                raise ReloadException(f"Invalid join request for existing user: {msg}")

            self.sockets[ws] = room
        elif ws not in self.sockets:
            raise ReloadException(f"Invalid message before joining: {msg}")
        else:
            room = self.sockets[ws]
            await room.handle_socket_msg(ws, msg_type, msg_data)

    async def disconnect_socket(self, ws):
        room = self.sockets.get(ws)
        if room is None:
            return

        await room.disconnect_socket(ws)

        if room.is_empty():
            del self.rooms[room.room_id]


server = Server()
