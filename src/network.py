import socketio as sio
import pygame
import enum
from flask import Flask
from abc import ABC, abstractmethod

server = sio.Server()
opponent_key = None

class GameMode(enum.Enum):
    CLIENT = 0
    SERVER = 1


class GameBase(ABC):
    network: sio.Server | sio.Client

    def connect(self, *args):
        print("connected:", args)

    def disconnect(self, *args):
        print("disconnected:", args)

    def move(self, key):
        self.network.emit("move", {"key": key})

    def opponent_move(self, sid: str | None, data: dict):
        if data["key"] is None:
            return

        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, {"key": data["key"]}))

    def reset_ball(self, starts_towards: str = "server"):
        self.network.emit("reset_ball")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 4, {"starts_towards": starts_towards}))

    def score(self, server_score: int, client_score: int):
        self.network.emit("score", {"server": server_score, "client": client_score})
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 3, {"server": server_score, "client": client_score}))

    @abstractmethod
    def run(self):
        pass


class GameServer(GameBase):
    def __init__(self):
        self.network = sio.Server()
        self.opponent_key = None
        self.network.on("connect", self.connect)
        self.network.on("disconnect", self.disconnect)
        self.network.on("move", self.opponent_move)
        self.app = Flask(__name__)
        self.app.wsgi_app = sio.WSGIApp(self.network, self.app.wsgi_app)

    def run(self):
        self.app.run(host="0.0.0.0", port=5000)

class GameClient(GameBase):
    def __init__(self):
        self.network = sio.Client()

        self.network.on("connect", self.connect)
        self.network.on("disconnect", self.disconnect)
        self.network.on("move", self.opponent_move)
        self.network.on("reset_ball", self.reset_ball)
        self.network.on("score", self.score)
        
        self.network.connect("http://localhost:5000")

    def score(self, data: dict):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 3, data))

    def opponent_move(self, data: dict):
        return super().opponent_move(None, data)

    def run(self):
        self.network.wait()