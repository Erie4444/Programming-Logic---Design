from config import *
from Socket_Client import SocketClient
from Dominoes_Logic import *
from threading import Thread
from util import *
import sys

class DominoesClient:
    def __init__(self):
        self.socket = SocketClient()
        self.name = input("Enter your name: ")
        self.status = "joining"
        print("Client: Connecting to server, please wait...")
        self.socket.connect()
        print("Client: Connected to server.")
        Thread(target=self.listenToServer, daemon=True).start()
        waitUntil(lambda: self.status != "joining")
        if self.status == "player":
            self.joinPlayer()
        elif self.status == "spectator":
            self.joinSpectator()
        self.updateLoop()
    
    def updateLoop(self):
        while self.status != "disconnected":
            self.update()
            time.sleep(0.1)  # Update every 100ms
        self.shutdown()

    def joinPlayer(self):
        print("Client: You are a player")
        input("Press Enter to join the game...")
        self.socket.sendMessage("joinPlayer", {"name": self.name})
    
    def joinSpectator(self):
        print("Client: You are a spectator")
        input("Press Enter to spectate the game...")
        self.socket.sendMessage("joinSpectator", {"name": self.name})

    def listenToServer(self):
        while self.socket.state == "connected":
            message = self.socket.receiveMessage()
            if message:
                print(f"Client: Received from server: {message}")
            if message:
                print("Client: received message")
                if message["type"] == "connectedPlayer":
                    self.status = "player"
                elif message["type"] == "connectedSpectator":
                    self.status = "spectator"
                elif message["type"] == "confirm":
                    print(f"Client: Server confirmation: {message['content']['message']}")
                elif message["type"] == "shutdown":
                    print("Client: Server is shutting down. Disconnecting...")
                    self.status = "disconnected"
                    self.socket.close()
    
    def update(self):
        pass
        
    def shutdown(self):
        self.status = "disconnected"
        self.socket.state = "disconnected"
        self.socket.close()
        sys.exit()


testClient = DominoesClient()