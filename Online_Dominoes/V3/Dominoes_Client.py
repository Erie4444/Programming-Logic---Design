from config import *
from Socket_Client import SocketClient
from Dominoes_Logic import *
from threading import Thread
from util import *
import sys

class DominoesClient:
    def __init__(self):
        self.socket = SocketClient()
        self.boardLeft = None
        self.boardRight = None
        self.name = input("Enter your name: ")
        self.status = "joining"
        self.playerNum = None
        self.waitingForResponse = False
        self.logic = None
        self.lastPlacedDomino = None
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
        if self.status == "player":
            waitUntil(lambda : self.logic != None)
            while self.status != "disconnected":
                self.update()
                time.sleep(0.1)  # Update every 100ms
                
        elif self.status == "spectator":
            while self.status != "disconnected":
                time.sleep(0.1)
        self.shutdown()

    def joinPlayer(self):
        print("Client: You are a player")
        input("Press Enter to join the game...")
        self.socket.sendMessage("join", {"type": "player", "name": self.name})
    
    def joinSpectator(self):
        print("Client: You are a spectator")
        input("Press Enter to spectate the game...")
        self.socket.sendMessage("join", {"type": "spectator"})
    
    def sendGameMessage(self,action,content):
        """
        Possible game messages from client:
         - sending over domino to place
        """
        if isinstance(content,Domino):
            content = content.deconstruct()
        self.socket.sendMessage("game",{"num":self.playerNum} | {"action":action,"content":content})

    def listenToServer(self):
        while self.socket.state == "connected":
            message = self.socket.receiveMessage()
            if message:
                if message["type"] == "connectedPlayer":
                    self.status = "player"

                elif message["type"] == "connectedSpectator":
                    self.status = "spectator"

                elif message["type"] == "confirm":
                    if message["content"] != "":
                        print(f"Client: Server confirmation, you are player {message['content']['playerCount']}")
                        if not self.playerNum:
                            self.playerNum = int(message['content']['playerCount'])
                    else:
                        print("Client: Server confirmation, you are a spectator")

                elif message["type"] == "shutdown":
                    print("Client: Server is shutting down. Disconnecting...")
                    self.status = "disconnected"
                    self.socket.close()

                elif message["type"] == "hand":
                    deconstructedHand = message["content"]
                    reconstructedHand = []
                    for domino in deconstructedHand:
                        print(domino)
                        temp = Domino(0,0)
                        temp.reconstruct(domino)
                        reconstructedHand.append(temp)
                    hand = Hand(reconstructedHand)
                    print("got hand",hand)
                    self.logic = ClientLogic(hand)
                    
                elif message["type"] == "placementFailure":
                    self.waitingForResponse = False
                    print("failed to place")
                    self.lastPlacedDomino = None
                    
                elif message["type"] == "placementSuccess":
                    self.waitingForResponse = False
                    self.logic.hand.removeDomino(self.lastPlacedDomino)
                    print("placement success")

                elif message["type"] == "win":
                    print("you win!")
                    
                elif message["type"] == "lose":
                    print("you lose...")
                
                elif message["type"] == "draw":
                    recvDomino = message["content"]
                    temp = Domino(0,0)
                    temp.reconstruct(recvDomino)
                    self.logic.hand.addDomino(temp)
                    self.waitingForResponse = False
                    
                elif message["type"] == "drawFailure":
                    print("nothing to draw from")
                    self.waitingForResponse = False

                elif message["type"] == "notYourTurn":
                    print("It is not your turn")
                    self.waitingForResponse = False
                
                elif message["type"] == "pips":
                    self.boardLeft = message["content"]["left"]
                    self.boardRight = message["content"]["right"]
                    self.waitingForResponse = False
                
                elif message["type"] == "noPips":
                    print("there are no dominos placed on the board")
                    self.waitingForResponse = False
                
                ##===spectator messages===
                elif message["type"] == "gameInfo":
                    board = message["content"]["board"]
                    for row in board:
                        print([str(i) for i in row])

    
    def update(self):
        waitUntil(lambda : self.waitingForResponse == False)
        if self.status == "player":
            print(self.logic.hand)
            self.textGUI()

    
    def textGUI(self):
        action = input("action >> ")
        if action == "place":
            dominoIndex = int(input("index >> "))
            side = input("side >> ")
            angle = int(input("angle >> "))
            coord = input("coord >> ").split(",")
            self.lastPlacedDomino = self.logic.hand.getList()[dominoIndex]
            self.lastPlacedDomino.angle = angle
            if side == "left":
                self.lastPlacedDomino.placeLeft(int(coord[0]),int(coord[1]))
            else:
                self.lastPlacedDomino.placeRight(int(coord[0]),int(coord[1]))

            domino = self.lastPlacedDomino.deconstruct()
            self.sendGameMessage("place",domino)
            self.waitingForResponse = True
        
        elif action == "draw":
            self.sendGameMessage("requestBoardPips","")
            self.waitingForResponse = True
            waitUntil(lambda:self.waitingForResponse == False)
            if not self.logic.hand.hasDominoWithPip(self.boardLeft) and not self.logic.hand.hasDominoWithPip(self.boardRight):
                self.sendGameMessage("draw","")
                self.waitingForResponse = True
            else:
                print("you have valid dominos")

        
    def shutdown(self):
        self.status = "disconnected"
        self.socket.state = "disconnected"
        self.socket.close()
        sys.exit()


testClient = DominoesClient()