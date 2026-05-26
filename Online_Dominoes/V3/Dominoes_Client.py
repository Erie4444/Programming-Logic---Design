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
        self.playerNum = None
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
        self.socket.sendMessage("join", {"type": "player", "name": self.name})
    
    def joinSpectator(self):
        print("Client: You are a spectator")
        input("Press Enter to spectate the game...")
        self.socket.sendMessage("join", {"type": "spectator"})
    
    def sendGameMessage(self,type,message):
        self.socket.sendMessage(type,{"num":self.playerNum} | message)


    def listenToServer(self):
        while self.socket.state == "connected":
            message = self.socket.receiveMessage()
            if message:
                if message["type"] == "connectedPlayer":
                    self.status = "player"

                elif message["type"] == "connectedSpectator":
                    self.status = "spectator"

                elif message["type"] == "confirm":
                    print(f"Client: Server confirmation, you are player {message['content']['playerCount']}")
                    if not self.playerNum:
                        self.playerNum = int(message['content']['playerCount'])

                elif message["type"] == "shutdown":
                    print("Client: Server is shutting down. Disconnecting...")
                    self.status = "disconnected"
                    self.socket.close()

                elif message["type"] == "hand":
                    ##get the hand yes
                    pass
    
    def update(self):
        if self.status == "player":
            pass
        pass
        
    def shutdown(self):
        self.status = "disconnected"
        self.socket.state = "disconnected"
        self.socket.close()
        sys.exit()


testClient = DominoesClient()