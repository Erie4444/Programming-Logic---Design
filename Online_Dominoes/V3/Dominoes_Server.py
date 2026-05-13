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
        self.players = []
        print("Server: Server initialized.")
        print("Server: Waiting for players to join...")
        self.listenThreads = []
        self.listenThread = Thread(target=self.listenToClients, daemon=True)
        self.acceptThread = Thread(target=self.socket.acceptClients, daemon=True)
        self.acceptThread.start()
        self.listenThread.start()
        self.gameLoop()
    
    def gameLoop(self):
        self.waitForPlayers()
        self.initGame()
        input("Press Enter to end the game...")
        self.shutdown()

    def waitForPlayers(self):
        waitUntil(lambda: len(self.socket.getClients()["PLAYERS"]) >= NUM_PLAYERS)
        print("Server: All players have connected. Waiting for players to join the game...")
        waitUntil(lambda: len(self.players) >= NUM_PLAYERS)
        print("Server: Starting the game!")
    
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
                    if message["type"] == "join":
                        if message["content"]["type"] == "player":
                            if len(self.players) < NUM_PLAYERS:
                                self.players.append(message["content"]["name"])
                                print(f"Server: Player joined: {message['content']['name']} (Total: {len(self.players)})")
                                self.socket.sendMessage(client, "confirm", {"playerCount": len(self.players)})
                            else:
                                self.socket.sendMessage(client, "decline", "")
                        elif message["content"]["type"] == "spectator":
                            print(f"Server: Spectator joined")
                            self.socket.sendMessage(client, "confirm", "")
                    # Here you would handle the message and update game state accordingly
    
    def initGame(self):
        ##start game here
        for playerIndex in range(len(self.players)):
            hand = [(domino.tuple()) for domino in self.game.players[playerIndex].hand.dominoes]
            self.socket.sendMessageToPlayer(playerIndex,"hand",hand)
    
    def status(self):
        self.socket.status()

    def shutdown(self):
        self.socket.broadcastMessage("shutdown", "")
        self.socket.close()
        sys.exit()
testServer = DominoesServer()