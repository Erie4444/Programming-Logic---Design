"""========RUN THIS FOR THE SERVER========="""

from config import *
from Socket_Server import SocketServer
from Dominoes_Logic import *
from threading import Thread
import sys
import time
from util import *

class DominoesServer:
    '''
    The Server code that is run
    '''
    def __init__(self):
        self.socket = SocketServer() ##instantiates a server socket
        self.players = []
        self.state = "waitingForPlayers"
        self.spectatorCount = 0
        self.waitingForResponse = False
        print("Server initialized.")
        ##has a listen thread for each client
        self.listenThreads = []
        ##starts threads to accept and recieve messages
        self.listenThread = Thread(target=self.listenToClients, daemon=True)
        self.acceptThread = Thread(target=self.socket.acceptClients, daemon=True)
        self.acceptThread.start()
        self.listenThread.start()
        self.gameLoop()
    
    def gameLoop(self):
        '''
        Main game loop
        '''
        while self.state != "close":
            if self.state == "waitingForPlayers":
                self.waitForPlayers()

            elif self.state == "initGame":
                self.initGame()

            elif self.state == "game":
                ##if player hands is full, which means all players have given their hadn when the game ended
                if len(self.playerHands) == len(self.socket.getClients()["PLAYERS"]):
                    self.state = "endgame"

            elif self.state == "endgame":
                self.socket.broadcastMessage("gameResult",self.playerHands)
                self.state = "end"

            elif self.state == "end":
                print("quit on one of the clients to close the game")
            time.sleep(0.1)

    def waitForPlayers(self):
        print("Waiting for players...")
        waitUntil(lambda: len(self.players) >= NUM_PLAYERS) ##waits until there are enough players
        self.socket.broadcastMessage("gameStart","")
        print("Starting Game")
        self.state = "initGame"
    
    def listenToClients(self):
        '''
        Thread run to listen to clients
        '''
        while self.socket.state == "running":
            listenLen = len(self.listenThreads) ##amount of listening threads
            clientLen = len(self.socket.getPlayers()+self.socket.getSpectators()) ##amount of clients
            if listenLen < clientLen: ##checks if the amount of threads is less than the clients
                for index in range(listenLen, clientLen): ##adds a new thread for each missing client
                    client = self.socket.getClientsList()[index]
                    self.listenThreads.append(Thread(target=self.parseClientMessages, args=(client,), daemon=True))
                    self.listenThreads[-1].start()
            time.sleep(0.5)  ## checks for new clients every 500ms
    
    def parseClientMessages(self, client):
        '''
        Thread to parse and handle messages from clients
        '''
        while self.socket.state == "running":
            message = self.socket.receiveMessage(client) ##gets the message from the client
            # print(f"Server: Received from {client.getpeername()}: {message}")
            if message:
                    if message["type"] == "join": ##clients joining the game
                        if message["content"]["type"] == "player": ##the client is trying to join as a player
                            if len(self.players) < NUM_PLAYERS: ##refuse if there are too many
                                self.players.append(message["content"]["name"])
                                print(f"{message['content']['name']} joined. {NUM_PLAYERS-len(self.players)} left")
                                self.socket.sendMessage(client, "confirm", {"playerCount": len(self.players)}) ##sends a confirmation of the join to the player

                            else:
                                self.socket.sendMessage(client, "decline", "") ##declines if there are too many players

                        elif message["content"]["type"] == "spectator":
                            print(f"Server: Spectator joined")
                            self.spectatorCount += 1
                            self.socket.sendMessage(client, "confirm", "") ##confirms the spectator join
                    
                    if message["type"] == "disconnectClient":
                        self.shutdown()
                    
                    if message["type"] == "game":
                        if message["content"]["action"] == "playerScore": ##clients sending their scores at the end of the game
                            self.playerHands[message["content"]["content"]["score"]] = message["content"]["content"]["name"]

                        elif message["content"]["action"] == "emptyHandNotif":
                            ##when a client has an empty hand, the game ends
                            self.socket.broadcastMessage("gameEnd","","PLAYERS")

                        elif message["content"]["num"] == self.logic.getCurrentPlayer(): ##if the correct player send a game action
                            if message["content"]["action"] == "place": ##to place a domino
                                recvDomino = Domino(0,0) ##temporary domino for received domino
                                recvDomino.reconstruct(message["content"]["content"]) ##reconstructs the domino that is sent over
                                placed = self.logic.placeDomino(recvDomino) ##tries to place the domino
                                if placed:
                                    self.socket.sendMessage(client,"placementSuccess","") ##sends a success message if it can place
                                    self.logic.nextPlayer() ##goes to the next player
                                    ##updates all clients with the new game state
                                    self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct(),"origin":self.logic.board.board.origin,"currentPlayer":self.logic.currentPlayer})
                                else:
                                    self.socket.sendMessage(client,"placementFailure","") ##send failure if domino failed to place

                            elif message["content"]["action"] == "placeDB": ##debug placement, not used
                                ##forces a place and doesn't proceed to next player, was used when trying to link the logic and UI together
                                recvDomino = Domino(0,0)
                                recvDomino.reconstruct(message["content"]["content"])
                                placed = self.logic.placeDominoDB(recvDomino)
                                self.logic.board.board.printBoard()
                                if placed:
                                    self.logic.nextPlayer()
                                    self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct(),"origin":self.logic.board.board.origin})
                            
                            elif message["content"]["action"] == "requestBoardPips": ##request to get the board ends
                                if self.logic.board.left and self.logic.board.right:
                                    self.socket.sendMessage(client,"pips",{"left":self.logic.board.left.pips,"right":self.logic.board.right.pips})
                                else:
                                    self.socket.sendMessage(client,"noPips","")
                            
                            elif message["content"]["action"] == "draw": ##request to draw a domino
                                drawnDomino = self.logic.drawDomino()
                                if drawnDomino: ##if there is a domino, send the domino
                                    self.socket.sendMessage(client,"draw",drawnDomino.deconstruct())
                                else: ##else send a failure message
                                    self.socket.sendMessage(client,"drawFailure","")
                        else:
                            self.socket.sendMessage(client,"notYourTurn","") ##tell client its not their turn
                        # self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct()},"SPECTATORS",self.spectatorCount)
    
    def initGame(self):
        ##initializing values
        self.playerHands = {}
        self.logic = ServerLogic()
        self.logic.initGame()
        ##dealing hands
        for i, hand in enumerate(self.logic.getHands()):
            deconstructedHand = [domino.deconstruct() for domino in hand.getList()] ##deconstructs the hand to send over
            self.socket.sendMessageToPlayer(i,"hand",deconstructedHand) ##sending the hand over
        ##sends a gameInfo to all players when game starts
        self.socket.broadcastMessage("gameInfo",{"board":self.logic.board.board.deconstruct(),"origin":self.logic.board.board.origin,"currentPlayer":self.logic.currentPlayer},"PLAYERS",)
        self.state = "game"

    def status(self):
        self.socket.status()

    def shutdown(self):
        '''
        Shuts down the server
        '''
        self.state = "close"
        self.socket.broadcastMessage("shutdown", "") ##tells all clients to shut down too
        self.socket.close()
        sys.exit()

server = DominoesServer()