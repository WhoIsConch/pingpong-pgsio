import socketio as sio
import pygame
import enum 

server = sio.Server()
opponent_key = None

class GameMode(enum.Enum):
    CLIENT = 0
    SERVER = 1

@server.event
def connect(sid, environ):
    print("connected", sid)

@server.event
def disconnect(sid):
    print("disconnected", sid)

@server.event
def move(sid, data):
    global opponent_key
    # Convert key to a pygame key
    # data["key"] is an integer representing the key
    pygame.event.post(pygame.event.Event("OPP", {"key": opponent_key}))
