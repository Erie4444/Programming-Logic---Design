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
        self.state = "waitingForPlayers"
        self.spectatorCount = 0
        self.waitingForResponse = False
        print("Server initialized.")
        self.listenThreads = []
        self.listenThread = Thread(target=self.listenToClients, daemon=True)
        self.acceptThread = Thread(target=self.socket.acceptClients, daemon=True)
        self.acceptThread.start()
        self.listenThread.start()
        self.gameLoop()
    
    def gameLoop(self):
        while self.state != "close":
            if self.state == "waitingForPlayers":
                self.waitForPlayers()
            elif self.state == "initGame":
                self.initGame()
            elif self.state == "game":
                if len(self.playerHands) == len(self.socket.getClients()["PLAYERS"]):
                    self.state = "endgame"
            elif self.state == "endgame":
                self.socket.broadcastMessage("gameResult",self.playerHands)
                self.state = "end"
            elif self.state == "end":
                input("Press Enter to close the server...")
                self.shutdown()
            time.sleep(0.1)

    def waitForPlayers(self):
        print("Waiting for players...")
        waitUntil(lambda: len(self.players) >= NUM_PLAYERS)
        print("Starting Game")
        self.state = "initGame"
    
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
            # print(f"Server: Received from {client.getpeername()}: {message}")
            if message:
                    if message["type"] == "join": ##clients joining the game
                        if message["content"]["type"] == "player":
                            if len(self.players) < NUM_PLAYERS:
                                self.players.append(message["content"]["name"])
                                print(f"{message['content']['name']} joined. {NUM_PLAYERS-len(self.players)} left")
                                self.socket.sendMessage(client, "confirm", {"playerCount": len(self.players)})
                            else:
                                self.socket.sendMessage(client, "decline", "")
                        elif message["content"]["type"] == "spectator":
                            print(f"Server: Spectator joined")
                            self.spectatorCount += 1
                            self.socket.sendMessage(client, "confirm", "")
                    
                    if message["type"] == "game":
                        if message["content"]["action"] == "playerScore": ##getting the score at the end of the game
                            self.playerHands[message["content"]["content"]["score"]] = message["content"]["content"]["name"]

                        elif message["content"]["action"] == "emptyHandNotif":
                            self.socket.broadcastMessage("gameEnd","","PLAYERS")

                        elif message["content"]["num"] == self.logic.getCurrentPlayer():
                            if message["content"]["action"] == "place":
                                recvDomino = Domino(0,0)
                                recvDomino.reconstruct(message["content"]["content"])
                                placed = self.logic.placeDomino(recvDomino)
                                if placed:
                                    self.socket.sendMessage(client,"placementSuccess","")
                                    self.logic.nextPlayer()
                                    self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct(),"origin":self.logic.board.board.origin},"PLAYERS")
                                else:
                                    self.socket.sendMessage(client,"placementFailure","")

                            elif message["content"]["action"] == "placeDB":
                                recvDomino = Domino(0,0)
                                recvDomino.reconstruct(message["content"]["content"])
                                placed = self.logic.placeDominoDB(recvDomino)
                                self.logic.board.board.printBoard()
                                if placed:
                                    self.logic.nextPlayer()
                                    self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct(),"origin":self.logic.board.board.origin},"PLAYERS")
                            
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
                        # self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct()},"SPECTATORS",self.spectatorCount)
    
    def initGame(self):
        self.playerHands = {}
        self.logic = ServerLogic()
        self.logic.initGame()
        for i, hand in enumerate(self.logic.getHands()):
            deconstructedHand = [domino.deconstruct() for domino in hand.getList()]
            self.socket.sendMessageToPlayer(i,"hand",deconstructedHand)
        self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct(),"origin":self.logic.board.board.origin},"PLAYERS")
        self.state = "game"

    def status(self):
        self.socket.status()

    def shutdown(self):
        self.state = "close"
        self.socket.broadcastMessage("shutdown", "")
        self.socket.close()
        sys.exit()
testServer = DominoesServer()