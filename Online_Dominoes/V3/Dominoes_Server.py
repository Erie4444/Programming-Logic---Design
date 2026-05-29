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
        self.logic = ServerLogic()
        self.players = []
        self.spectatorCount = 0
        self.waitingForResponse = False
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
                            self.spectatorCount += 1
                            self.socket.sendMessage(client, "confirm", "")
                    
                    if message["type"] == "game":
                        if message["content"]["num"] == self.logic.getCurrentPlayer():
                            if message["content"]["action"] == "place":
                                recvDomino = Domino(0,0)
                                recvDomino.reconstruct(message["content"]["content"])
                                placed = self.logic.placeDomino(recvDomino)
                                if placed:
                                    self.socket.sendMessage(client,"placementSuccess","")
                                    self.logic.nextPlayer()
                                else:
                                    self.socket.sendMessage(client,"placementFailure","")
                                self.logic.board.board.printBoard()
                                print(self.logic.boneyard)
                                print(f"spectators: {self.spectatorCount}")
                            
                            elif message["content"]["action"] == "requestBoardPips":
                                if self.logic.board.left and self.logic.board.right:
                                    self.socket.sendMessage(client,"pips",{"left":self.logic.board.left.pips,"right":self.logic.board.right.pips})
                                else:
                                    self.socket.sendMessage(client,"noPips","")
                            
                            elif message["content"]["action"] == "draw":
                                drawnDomino = self.logic.drawDomino()
                                if drawnDomino:
                                    self.socket.sendMessage(client,"draw",drawnDomino.deconstruct())
                                else:
                                    self.socket.sendMessage(client,"drawFailure","")
                        else:
                            self.socket.sendMessage(client,"notYourTurn","")
                        

                        self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct()},"SPECTATORS",self.spectatorCount)
    
    def initGame(self):
        self.logic.initGame()
        for i, hand in enumerate(self.logic.getHands()):
            deconstructedHand = [domino.deconstruct() for domino in hand.getList()]
            self.socket.sendMessageToPlayer(i,"hand",deconstructedHand)

    def status(self):
        self.socket.status()

    def shutdown(self):
        self.socket.broadcastMessage("shutdown", "")
        self.socket.close()
        sys.exit()
testServer = DominoesServer()