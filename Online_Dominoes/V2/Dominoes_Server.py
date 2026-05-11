from config import *
from Socket_Server import SocketServer
from Dominoes_Logic import *
from threading import Thread
import sys
import time
from util import *

class DominoesServer:
    def __init__(self):
        self.socket = SocketServer()
        self.joinedPlayers = 0
        print("Server: Server initialized.")
        print("Server: Waiting for players to join...")
        self.listenThreads = []
        self.listenThread = Thread(target=self.listenToClients, daemon=True)
        self.acceptThread = Thread(target=self.socket.acceptClients, daemon=True)
        self.acceptThread.start()
        self.listenThread.start()
        self.waitForPlayers()
    
    def waitForPlayers(self):
        waitUntil(lambda: len(self.socket.getClients()["PLAYERS"]) >= NUM_PLAYERS)
        print("Server: All players have joined. Waiting for confirmation to start the game...")
        waitUntil(lambda: self.joinedPlayers >= NUM_PLAYERS)
        print("Server: Starting the game!")
        input("Press Enter to stop the server...")
        self.shutdown()
    
    def listenToClients(self):
        while self.socket.state == "running":
            listenLen = len(self.listenThreads)
            clientLen = len(self.socket.getPlayers()+self.socket.getSpectators())
            if listenLen < clientLen:
                for index in range(listenLen, clientLen):
                    client = self.socket.getClientsList()[index]
                    self.listenThreads.append(Thread(target=self.parseClientMessages, args=(client,), daemon=True))
                    self.listenThreads[-1].start()
            time.sleep(0.5)  # Check for new clients every 500ms
    
    def parseClientMessages(self, client):
        while self.socket.state == "running":
            message = self.socket.receiveMessage(client)
            print(f"Server: Received from {client.getpeername()}: {message}")
            if message:
                    if message["type"] == "joinPlayer":
                        if self.joinedPlayers < NUM_PLAYERS:
                            self.joinedPlayers += 1
                            print(f"Server: Player joined: {message['content']['name']} (Total: {self.joinedPlayers})")
                            # time.sleep(1)
                            self.socket.sendMessage(client, "confirm", {"message": f"Welcome {message['content']['name']}! Waiting for other players..."})
                        else:
                            self.socket.sendMessage(client, "decline", {"message": "Game is full. Please try again later."})
                    elif message["type"] == "joinSpectator":
                        print(f"Server: Spectator joined: {message['content']['name']}")
                        self.socket.sendMessage(client, "confirm", {"message": f"Welcome {message['content']['name']}! You are now spectating the game."})
                    # Here you would handle the message and update game state accordingly

    def shutdown(self):
        self.socket.broadcastMessage("shutdown", {"message": "Server is shutting down. Please disconnect."})
        self.socket.close()
        sys.exit()
testServer = DominoesServer()