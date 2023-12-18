import socketio as sio
import pygame
import enum
from flask import Flask

server = sio.Server()
opponent_key = None

class GameMode(enum.Enum):
    CLIENT = 0
    SERVER = 1

class GameServer:
    def __init__(self):
        self.server = sio.Server()
        self.opponent_key = None
        self.server.on("connect", self.connect)
        self.server.on("disconnect", self.disconnect)
        self.server.on("move", self.opponent_move)
        self.app = Flask(__name__)
        self.app.wsgi_app = sio.WSGIApp(self.server, self.app.wsgi_app)
        # print the address of the server

    def connect(self, sid, environ):
        print("connected", sid)

    def disconnect(self, sid):
        print("disconnected", sid)

    def move(self, key):
        self.server.emit("move", {"key": key})

    def opponent_move(self, sid, data: dict):
        if data["key"] is None:
            return

        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, {"key": data["key"]}))

    def move_ball(self, position: tuple):
        self.server.emit("move_ball", {"position": position})

    def run(self):
        self.app.run()

class GameClient:
    def __init__(self):
        self.client = sio.Client()

        self.client.on("connect", self.connect)
        self.client.on("disconnect", self.disconnect)
        self.client.on("move", self.opponent_move)
        self.client.on("move_ball", self.move_ball)
        
        self.client.connect("http://localhost:5000")

    def connect(self):
        print("connected")

    def disconnect(self):
        print("disconnected")

    def opponent_move(self, data: dict):
        if data["key"] is None:
            return
        
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, {"key": data["key"]}))

    def move(self, key):
        self.client.emit("move", {"key": key})

    def move_ball(self, data: dict):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 2, {"position": data["position"]}))

    def run(self):
        self.client.wait()